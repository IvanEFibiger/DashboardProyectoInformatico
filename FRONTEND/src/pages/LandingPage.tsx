import ScrollTopButton from "../shared/ScrollTopButton";

export default function LandingPage() {
  return (
    <>
      {}
      <section id="hero" className="mx-auto max-w-6xl px-4 pt-10">
        <div className="rounded-[28px] shadow-lg ring-1 ring-black/5 overflow-hidden">
          <div className="relative overflow-hidden bg-gradient-to-b from-[#0ea5e9] via-[#2563eb] to-slate-900 text-white">
            <div className="px-6 md:px-10 py-16 md:py-20">
              <div className="flex flex-col items-center text-center">
                <img
                  src="/img/id_logo_rounded_120.png"
                  alt="ID Smart Solutions"
                  className="h-30 w-auto md:h-60"
                />
                <h1 className="text-3xl md:text-5xl font-extrabold tracking-wide text-center text-[#F59E0B]">
                  ID SMART SOLUTIONS
                </h1>
                <p className="mt-4 text-slate-200 max-w-2xl">
                  Software, infraestructura y soporte con foco en{" "}
                  <span className="text-[#f59e0b] font-semibold">seguridad</span> y resultados.
                </p>
                <div className="mt-8 flex flex-col sm:flex-row gap-3">
                  <a
                    href="#services"
                    className="inline-flex items-center justify-center rounded-xl bg-white/10 px-5 py-2.5 ring-1 ring-white/20 hover:bg-white/15"
                  >
                    Ver servicios
                  </a>
                  <a
                    href="#contact"
                    className="inline-flex items-center justify-center rounded-xl bg-[#f59e0b] px-5 py-2.5 font-semibold text-slate-900 hover:brightness-95"
                  >
                    Pedir una consulta
                  </a>
                </div>
              </div>

              {}
              <div className="mt-12 grid grid-cols-1 md:grid-cols-4 gap-6">
                {[
                  { icon: "deployed_code", title: "Software a medida", desc: "APIs y apps escalables, seguras y mantenibles." },
                  { icon: "cloud_upload", title: "Infraestructura", desc: "Cloud, redes y automatización con mejores prácticas." },
                  { icon: "web", title: "Web & Apps", desc: "Sitios y aplicaciones modernas, rápidas y accesibles." },
                  { icon: "security", title: "Soporte & Sec", desc: "Monitoreo, hardening y respuesta ante incidentes." },
                ].map((c, i) => (
                  <div key={i} className="rounded-xl bg-white/5 p-6 ring-1 ring-white/10">
                    <span className="material-symbols-outlined block text-4xl mb-2 text-white/90">
                      {c.icon}
                    </span>
                    <h3 className="font-semibold">{c.title}</h3>
                    <p className="text-sm text-slate-200/90 mt-1">{c.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {}
      <section id="nosotros" className="mx-auto max-w-6xl px-4 py-16">
        <div className="rounded-[28px] shadow-lg ring-1 ring-black/5 overflow-hidden bg-white">
          <div className="px-6 md:px-10 py-12">
            <h2 className="text-2xl font-bold mb-6 text-slate-900">Nosotros</h2>
            <div className="grid md:grid-cols-2 gap-8 items-center">
              <img
                src="/img/imagen-nosotros.jpg"
                alt="Nosotros"
                className="rounded-2xl shadow-md"
              />
              <div>
                <p className="text-slate-700 leading-relaxed">
                  Acompañamos a PYMEs y organismos desde la idea hasta la operación,
                  con entregas iterativas, medición de resultados y{" "}
                  <span className="font-medium text-slate-900">seguridad por diseño</span>.
                </p>
                <ul className="mt-4 grid sm:grid-cols-2 gap-2 text-sm text-slate-700">
                  <li className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-[#10b981]">check_circle</span>
                    Desarrollo y APIs
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-[#10b981]">check_circle</span>
                    Infraestructura & Cloud
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-[#10b981]">check_circle</span>
                    Web & Mobile
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-[#10b981]">check_circle</span>
                    Ciberseguridad & Soporte
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {}
      <section id="services" className="mx-auto max-w-6xl px-4 pb-16">
        <div className="rounded-[28px] shadow-lg ring-1 ring-black/5 overflow-hidden bg-white">
          <div className="px-6 md:px-10 py-12">
            <h2 className="text-2xl font-bold mb-8 text-slate-900">Servicios</h2>
            <div className="grid md:grid-cols-3 gap-8">
              {[
                {
                  img: "/img/servicioTecnico.jpg",
                  title: "Soporte & Ciberseguridad",
                  desc: "Mantenimiento preventivo, hardening, inventario y respuesta a incidentes.",
                },
                {
                  img: "/img/diseño-web.jpg",
                  title: "Web, Marketing y Apps",
                  desc: "Sitios corporate, landings, e-commerce y apps integradas a tus procesos.",
                },
                {
                  img: "/img/solucionesIt.jpg",
                  title: "Soluciones IT",
                  desc: "Integración de sistemas, automatización y despliegues en cloud/on-prem.",
                },
              ].map((card, i) => (
                <article key={i} className="group rounded-2xl border border-slate-200 overflow-hidden bg-white">
                  <div className="relative">
                    <img src={card.img} className="w-full h-48 object-cover" />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition" />
                  </div>
                  <div className="p-5">
                    <h3 className="font-semibold">{card.title}</h3>
                    <p className="text-sm text-slate-600 mt-1">{card.desc}</p>
                    <div className="mt-4">
                      <a
                        href="#contact"
                        className="inline-flex items-center justify-center rounded-xl bg-gradient-to-r from-[#2563eb] to-[#0ea5e9] px-4 py-2 text-sm font-semibold text-white shadow-sm hover:opacity-95 active:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2563eb]"
                      >
                        Consultar
                      </a>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </div>
      </section>

      {}
      <section id="contact" className="mx-auto max-w-6xl px-4 pb-16">
        <div className="rounded-[28px] shadow-lg ring-1 ring-black/5 overflow-hidden bg-white">
          <div className="px-6 md:px-10 py-12">
            <div className="grid md:grid-cols-2 gap-8">
              <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
  <h3 className="text-lg font-semibold mb-4">Contacto</h3>

  <form
    className="space-y-5"
    onSubmit={(e) => {
      e.preventDefault();
      alert("Enviar al backend /contact");
    }}
  >
    {}
    <div>
      <label htmlFor="name" className="block text-sm font-medium text-slate-700 mb-1">
        Nombre
      </label>
      <input
        id="name"
        name="name"
        required
        placeholder="Tu nombre"
        className="block w-full rounded-xl border border-slate-300/70 bg-white px-3 py-2.5 text-slate-900 placeholder-slate-400 shadow-sm
                   focus:border-[#2563eb] focus:ring-4 focus:ring-[#2563eb]/20 outline-none"
      />
    </div>

    {}
    <div className="grid gap-5 md:grid-cols-2">
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-slate-700 mb-1">
          Email
        </label>
        <input
          id="email"
          name="email"
          type="email"
          required
          placeholder="tu@correo.com"
          className="block w-full rounded-xl border border-slate-300/70 bg-white px-3 py-2.5 text-slate-900 placeholder-slate-400 shadow-sm
                     focus:border-[#2563eb] focus:ring-4 focus:ring-[#2563eb]/20 outline-none"
        />
      </div>

      <div>
        <label htmlFor="phone" className="block text-sm font-medium text-slate-700 mb-1">
          Teléfono
        </label>
        <input
          id="phone"
          name="phone"
          placeholder="+54 9 ..."
          className="block w-full rounded-xl border border-slate-300/70 bg-white px-3 py-2.5 text-slate-900 placeholder-slate-400 shadow-sm
                     focus:border-[#2563eb] focus:ring-4 focus:ring-[#2563eb]/20 outline-none"
        />
      </div>
    </div>

    {}
    <div>
      <label htmlFor="message" className="block text-sm font-medium text-slate-700 mb-1">
        Mensaje
      </label>
      <textarea
        id="message"
        name="message"
        rows={5}
        required
        placeholder="Contame qué necesitás…"
        className="block w-full rounded-xl border border-slate-300/70 bg-white px-3 py-2.5 text-slate-900 placeholder-slate-400 shadow-sm
                   focus:border-[#2563eb] focus:ring-4 focus:ring-[#2563eb]/20 outline-none resize-y"
      />
    </div>


    <div className="pt-2">
      <button
        type="submit"
        className="w-full sm:w-auto inline-flex items-center justify-center rounded-xl bg-[#f59e0b] px-5 py-2.5
                   font-semibold text-slate-900 shadow-sm hover:brightness-95 focus:outline-none
                   focus:ring-4 focus:ring-[#f59e0b]/30"
      >
        Enviar
      </button>
    </div>
  </form>
</article>

              <article className="rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
                <h3 className="text-lg font-semibold p-6 pb-0">¿Dónde encontrarnos?</h3>
                <iframe
                  className="w-full h-[360px]"
                  src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d765.0097024708249!2d-62.61860115054805!3d-39.918147678288165!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x95f3cfa98d29f2c5%3A0x211d4f27f2d0e2a6!2sID%20Soluciones%20Inform%C3%A1ticas!5e0!3m2!1ses!2sar!4v1697912455839!5m2!1ses!2sar"
                  loading="lazy"
                  allowFullScreen
                  referrerPolicy="no-referrer-when-downgrade"
                  title="Ubicación ID Smart Solutions"
                />
              </article>
            </div>
          </div>
        </div>
      </section>

      <footer className="border-t border-slate-200 py-6">
        <div className="mx-auto max-w-6xl px-4 flex flex-col sm:flex-row items-center justify-between gap-3 text-sm text-slate-600">
          <span>© {new Date().getFullYear()} ID Smart Solutions</span>
          <span className="flex items-center gap-1">
            <span className="material-symbols-outlined text-[#f59e0b]">code</span>
            Hecho con buenas prácticas y seguridad.
          </span>
        </div>
      </footer>

      <ScrollTopButton />
    </>
  );
}
