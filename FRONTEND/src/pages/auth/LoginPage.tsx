import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../../services/auth.service";

const STORAGE_EMAIL_KEY = "idsmart.email"; 

export const LoginPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPwd, setShowPwd] = useState(false);
  const [remember, setRemember] = useState(false);
  const [loadingFill, setLoadingFill] = useState(true);

  const navigate = useNavigate();

  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_EMAIL_KEY);
      if (saved) {
        setEmail(saved);
        setRemember(true);
      }
    } finally {
      setLoadingFill(false);
    }
  }, []);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await login(email, password);

      if (remember) localStorage.setItem(STORAGE_EMAIL_KEY, email);
      else localStorage.removeItem(STORAGE_EMAIL_KEY);

      navigate("/dashboard");
    } catch (err) {
      console.error(err);
      alert("Login fallido");
    }
  }

  function onForget() {
    localStorage.removeItem(STORAGE_EMAIL_KEY);
    setRemember(false);
  }

  return (
    <div className="min-h-screen w-full bg-gradient-to-b from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="rounded-2xl border border-slate-200/60 dark:border-slate-800/60 bg-white/90 dark:bg-slate-900/70 backdrop-blur shadow-lg">
          <div className="px-6 sm:px-8 py-8">
            <div className="flex flex-col items-center text-center">
              <img src="/img/id_logo_rounded_120.png" alt="ID Smart Solutions" className="h-16 w-16" />
              <h1 className="mt-3 text-xl font-bold tracking-tight text-slate-900 dark:text-slate-50">Iniciar sesión</h1>
              <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">Accedé con tu correo y clave</p>
            </div>

            <form onSubmit={onSubmit} className="mt-6 space-y-5">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Email
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="username"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="tu@correo.com"
                  className="block w-full rounded-xl border border-slate-300/80 dark:border-slate-700/70 bg-white dark:bg-slate-900 px-3 py-2.5 text-slate-900 dark:text-slate-100 placeholder-slate-400 shadow-sm focus:border-[#2563eb] focus:ring-4 focus:ring-[#2563eb]/20 outline-none"
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Clave
                </label>
                <div className="relative">
                  <input
                    id="password"
                    name="password"
                    type={showPwd ? "text" : "password"}
                    autoComplete="current-password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="block w-full rounded-xl border border-slate-300/80 dark:border-slate-700/70 bg-white dark:bg-slate-900 px-3 py-2.5 pr-12 text-slate-900 dark:text-slate-100 placeholder-slate-400 shadow-sm focus:border-[#2563eb] focus:ring-4 focus:ring-[#2563eb]/20 outline-none"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPwd((s) => !s)}
                    aria-label={showPwd ? "Ocultar clave" : "Mostrar clave"}
                    className="absolute inset-y-0 right-0 flex items-center px-3 text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
                    tabIndex={-1}
                  >
                    <span className="material-symbols-outlined text-xl">
                      {showPwd ? "visibility_off" : "visibility"}
                    </span>
                  </button>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <label className="inline-flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
                  <input
                    type="checkbox"
                    className="h-4 w-4 rounded border-slate-300 text-[#2563eb] focus:ring-[#2563eb]"
                    checked={remember}
                    onChange={(e) => setRemember(e.target.checked)}
                    disabled={loadingFill}
                  />
                  Recordar email
                </label>

                <button
                  type="button"
                  onClick={onForget}
                  className="text-xs text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 underline underline-offset-2"
                >
                  Olvidar email
                </button>
              </div>

              <button
                type="submit"
                disabled={loadingFill}
                className="w-full inline-flex items-center justify-center rounded-xl bg-gradient-to-r from-[#2563eb] to-[#0ea5e9] px-5 py-2.5 font-semibold text-white shadow-sm hover:opacity-95 active:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563eb] transition disabled:opacity-60"
              >
                Ingresar
              </button>
            </form>
          </div>
        </div>

        <p className="mt-4 text-center text-[11px] leading-snug text-slate-500 dark:text-slate-400 px-2">
          Tip de seguridad: evitá recordar contraseñas en dispositivos compartidos. Preferí el gestor del navegador.
        </p>

        <p className="mt-2 text-center text-xs text-slate-500 dark:text-slate-400">
          © {new Date().getFullYear()} ID Smart Solutions
        </p>
      </div>
    </div>
  );
};
