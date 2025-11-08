# api/db/bootstrap.py
from api.db.db import mysql
import MySQLdb

MIGRATIONS = [

    (1, """
    CREATE TABLE IF NOT EXISTS usuarios (
        id        INT AUTO_INCREMENT PRIMARY KEY,
        `user`    VARCHAR(50)  NOT NULL,
        email     VARCHAR(120) NOT NULL,
        password  VARCHAR(255) NOT NULL,
        activo    TINYINT(1)   NOT NULL DEFAULT 1,
        UNIQUE KEY uq_usuarios_email (email)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

    CREATE TABLE IF NOT EXISTS clientes (
        id          INT AUTO_INCREMENT PRIMARY KEY,
        nombre      VARCHAR(120) NOT NULL,
        email       VARCHAR(120),
        direccion   VARCHAR(255),
        cuit        VARCHAR(20)  NOT NULL,
        id_usuario  INT NOT NULL,
        activo      TINYINT(1) NOT NULL DEFAULT 1,
        CONSTRAINT fk_clientes_usuario
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
            ON DELETE CASCADE,
        UNIQUE KEY uq_clientes_usuario_cuit (id_usuario, cuit),
        KEY idx_clientes_usuario (id_usuario)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

    CREATE TABLE IF NOT EXISTS productos (
        id          INT AUTO_INCREMENT PRIMARY KEY,
        nombre      VARCHAR(120) NOT NULL,
        descripcion TEXT,
        precio      DECIMAL(14,2) NOT NULL DEFAULT 0,
        cantidad    INT NOT NULL DEFAULT 0,
        id_usuario  INT NOT NULL,
        activo      TINYINT(1) NOT NULL DEFAULT 1,
        CONSTRAINT fk_productos_usuario
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
            ON DELETE CASCADE,
        UNIQUE KEY uq_productos_usuario_nombre (id_usuario, nombre),
        KEY idx_productos_usuario (id_usuario)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

    CREATE TABLE IF NOT EXISTS servicios (
        id          INT AUTO_INCREMENT PRIMARY KEY,
        nombre      VARCHAR(120) NOT NULL,
        descripcion TEXT,
        precio      DECIMAL(14,2) NOT NULL DEFAULT 0,
        id_usuario  INT NOT NULL,
        activo      TINYINT(1) NOT NULL DEFAULT 1,
        CONSTRAINT fk_servicios_usuario
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
            ON DELETE CASCADE,
        UNIQUE KEY uq_servicios_usuario_nombre (id_usuario, nombre),
        KEY idx_servicios_usuario (id_usuario)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

    CREATE TABLE IF NOT EXISTS factura (
        id            INT AUTO_INCREMENT PRIMARY KEY,
        fecha_emision DATETIME NOT NULL,
        id_clientes   INT NOT NULL,
        id_usuario    INT NOT NULL,
        total         DECIMAL(14,2) NOT NULL DEFAULT 0,
        CONSTRAINT fk_factura_cliente
            FOREIGN KEY (id_clientes) REFERENCES clientes(id)
            ON DELETE RESTRICT,
        CONSTRAINT fk_factura_usuario
            FOREIGN KEY (id_usuario)  REFERENCES usuarios(id)
            ON DELETE CASCADE,
        KEY idx_factura_usuario (id_usuario),
        KEY idx_factura_cliente (id_clientes)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

    CREATE TABLE IF NOT EXISTS detalle_factura (
        id              INT AUTO_INCREMENT PRIMARY KEY,
        id_factura      INT NOT NULL,
        id_producto     INT NULL,
        id_servicio     INT NULL,
        cantidad        INT NOT NULL,
        precio_unitario DECIMAL(14,2) NOT NULL,
        subtotal        DECIMAL(14,2) NOT NULL,
        CONSTRAINT fk_detalle_factura
            FOREIGN KEY (id_factura) REFERENCES factura(id)
            ON DELETE CASCADE,
        CONSTRAINT fk_detalle_producto
            FOREIGN KEY (id_producto) REFERENCES productos(id)
            ON DELETE RESTRICT,
        CONSTRAINT fk_detalle_servicio
            FOREIGN KEY (id_servicio) REFERENCES servicios(id)
            ON DELETE RESTRICT,
        -- En MySQL < 8.0 el CHECK se ignora
        CONSTRAINT chk_item_producto_o_servicio
            CHECK (
                (id_producto IS NOT NULL AND id_servicio IS NULL) OR
                (id_producto IS NULL AND id_servicio IS NOT NULL)
            ),
        KEY idx_detalle_factura (id_factura),
        KEY idx_detalle_producto (id_producto),
        KEY idx_detalle_servicio (id_servicio)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

    CREATE TABLE IF NOT EXISTS movimiento_stock (
        id          INT AUTO_INCREMENT PRIMARY KEY,
        producto_id INT NOT NULL,
        tipo        ENUM('entrada','salida') NOT NULL,
        cantidad    INT NOT NULL,
        fecha       DATETIME NOT NULL,
        stock_real  INT NOT NULL,
        CONSTRAINT fk_mov_stock_producto
            FOREIGN KEY (producto_id) REFERENCES productos(id)
            ON DELETE CASCADE,
        KEY idx_mov_stock_producto (producto_id),
        KEY idx_mov_stock_fecha (fecha)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """),

 
    (2, "-- índices extra manejados por ensure_indexes()"),


    (3, """
    CREATE TABLE IF NOT EXISTS refresh_tokens (
      jti        CHAR(36)    PRIMARY KEY,
      user_id    INT         NOT NULL,
      expires_at DATETIME    NOT NULL,
      revoked    TINYINT(1)  NOT NULL DEFAULT 0,
      created_at DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
      INDEX idx_refresh_user (user_id),
      INDEX idx_refresh_expires (expires_at),
      CONSTRAINT fk_refresh_user
        FOREIGN KEY (user_id) REFERENCES usuarios(id)
        ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """),
]

def _ensure_schema_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INT PRIMARY KEY,
            applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

def _applied_versions(cur):
    cur.execute("SELECT version FROM schema_migrations ORDER BY version")
    rows = cur.fetchall()
    versions = set()
    for row in rows:
        if isinstance(row, dict):
            versions.add(int(row.get("version")))
        else:
            versions.add(int(row[0]))
    return versions

def _apply_sql_block(cur, sql: str):

    statements = [s.strip() for s in sql.split(';') if s.strip()]
    for stmt in statements:
        cur.execute(stmt)

def _apply_migration(cur, version, sql):
    if sql.strip() and not sql.strip().startswith("--"):
        _apply_sql_block(cur, sql)
    cur.execute("INSERT INTO schema_migrations (version) VALUES (%s)", (version,))

def _index_exists(cur, table_name: str, index_name: str) -> bool:
    cur.execute("""
        SELECT 1
        FROM information_schema.statistics
        WHERE table_schema = DATABASE()
          AND table_name = %s
          AND index_name = %s
        LIMIT 1
    """, (table_name, index_name))
    return cur.fetchone() is not None

def _create_index_if_missing(cur, table: str, index: str, columns: str):
    if not _index_exists(cur, table, index):
        cur.execute(f"CREATE INDEX {index} ON {table} ({columns})")

def ensure_indexes(cur):

    _create_index_if_missing(cur, "factura",         "idx_factura_usuario_total",    "id_usuario, total")
    _create_index_if_missing(cur, "detalle_factura", "idx_detalle_factura_prod",     "id_producto, cantidad")
    _create_index_if_missing(cur, "detalle_factura", "idx_detalle_factura_serv",     "id_servicio, cantidad")


    _create_index_if_missing(cur, "refresh_tokens",  "idx_refresh_user_revoked",     "user_id, revoked")
    _create_index_if_missing(cur, "refresh_tokens",  "idx_refresh_user_exp",         "user_id, expires_at")

def run_bootstrap():
    conn = mysql.connection
    cur = conn.cursor() 
    try:
        _ensure_schema_table(cur)
        conn.commit()

        applied = _applied_versions(cur)

        for version, sql in MIGRATIONS:
            if version in applied:
                continue
            _apply_migration(cur, version, sql)
            conn.commit()

 
        ensure_indexes(cur)
        conn.commit()

    except MySQLdb.Error:
        conn.rollback()
        raise
    finally:
        cur.close()
