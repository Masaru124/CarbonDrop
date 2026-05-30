import {
  AlertTriangle,
  ArrowRight,
  BarChart3,
  BatteryCharging,
  Bike,
  BrainCircuit,
  CloudRain,
  Leaf,
  LineChart,
  MapPin,
  Recycle,
  Route,
  ScanSearch,
  ShieldCheck,
  Sparkles,
  Smartphone,
  Trash2,
  Truck,
  UtensilsCrossed,
  Zap,
} from "lucide-react";

const processSteps = [
  {
    title: "Capture",
    description: "Users upload bills, receipts, or trip details from mobile or desktop.",
    icon: Smartphone,
  },
  {
    title: "Read",
    description: "OCR, parsing, and document classification extract activity data.",
    icon: ScanSearch,
  },
  {
    title: "Estimate",
    description: "The carbon engine maps items to emission factors and computes totals.",
    icon: BarChart3,
  },
  {
    title: "Act",
    description: "Users receive a carbon budget, simulation insights, and reduction tips.",
    icon: Leaf,
  },
];

const moduleCards = [
  {
    title: "Food",
    icon: UtensilsCrossed,
    text: "Meal-aware emission estimates for groceries, packaged items, and eating habits.",
  },
  {
    title: "Transport",
    icon: Truck,
    text: "Travel choices translated into fuel, ride, and distance-based carbon impact.",
  },
  {
    title: "Energy",
    icon: BatteryCharging,
    text: "Home electricity use is tracked against a personal budget and monthly target.",
  },
  {
    title: "Waste",
    icon: Trash2,
    text: "Waste habits and recycling opportunities are surfaced as actionable reductions.",
  },
  {
    title: "Local Choices",
    icon: Bike,
    text: "Regional and low-impact alternatives help users swap high-carbon routines.",
  },
  {
    title: "Automation",
    icon: BrainCircuit,
    text: "Recommendations and simulations adapt to user behavior and emission history.",
  },
];

const benefits = [
  "Instant carbon visibility from everyday documents",
  "Personalized guidance instead of generic sustainability advice",
  "Scenario simulation before the user changes behavior",
  "A gamified dashboard that keeps progress measurable and motivating",
];

const applications = [
  {
    title: "Household Carbon Budgeting",
    icon: ShieldCheck,
    text: "Track monthly footprint across food, travel, energy, and waste.",
  },
  {
    title: "Campus and Community Programs",
    icon: MapPin,
    text: "Use the platform for awareness campaigns, audits, and impact reporting.",
  },
  {
    title: "What-If Planning",
    icon: Route,
    text: "Compare emissions before and after switching habits, routes, or products.",
  },
  {
    title: "Sustainable Operations",
    icon: Recycle,
    text: "Give teams a way to see carbon-heavy patterns and prioritize reductions.",
  },
];

function SectionTitle({ eyebrow, title, subtitle }) {
  return (
    <div className="mb-4">
      <p className="text-xs uppercase tracking-[0.35em] text-cyan-200/80">{eyebrow}</p>
      <h2 className="mt-2 text-[1.15rem] font-extrabold uppercase tracking-[0.2em] text-white">
        {title}
      </h2>
      {subtitle ? <p className="mt-2 text-sm leading-relaxed text-slate-200/75">{subtitle}</p> : null}
    </div>
  );
}

function StatCard({ value, label, tone = "cyan" }) {
  const toneClasses =
    tone === "green"
      ? "from-emerald-400/20 to-emerald-500/5 border-emerald-300/25 text-emerald-100"
      : tone === "amber"
        ? "from-amber-400/20 to-amber-500/5 border-amber-300/25 text-amber-100"
        : "from-cyan-400/20 to-sky-500/5 border-cyan-300/25 text-cyan-100";

  return (
    <div className={`rounded-2xl border bg-gradient-to-br p-4 shadow-[0_18px_40px_rgba(0,0,0,0.25)] ${toneClasses}`}>
      <div className="text-3xl font-black leading-none tracking-tight">{value}</div>
      <div className="mt-2 text-[0.72rem] font-semibold uppercase tracking-[0.28em] text-white/70">{label}</div>
    </div>
  );
}

function PosterPanel({ children, className = "" }) {
  return (
    <section
      className={`rounded-[1.4rem] border border-white/10 bg-white/6 p-4 shadow-[0_16px_40px_rgba(0,0,0,0.35)] backdrop-blur-sm ${className}`}
    >
      {children}
    </section>
  );
}

function WorkflowArrow() {
  return (
    <div className="hidden h-10 items-center justify-center lg:flex">
      <ArrowRight className="h-6 w-6 text-cyan-200/80" />
    </div>
  );
}

export default function Poster() {
  return (
    <div className="min-h-screen bg-[#04111e] text-white">
      <div className="relative overflow-hidden bg-[radial-gradient(circle_at_top,_rgba(56,189,248,0.22),_transparent_30%),radial-gradient(circle_at_bottom_right,_rgba(16,185,129,0.18),_transparent_28%),linear-gradient(180deg,#071524_0%,#04111e_42%,#071827_100%)] px-3 py-3 md:px-6 md:py-6">
        <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(115deg,transparent_0%,rgba(255,255,255,0.04)_35%,transparent_55%)] opacity-60" />
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(255,255,255,0.08),transparent_14%),radial-gradient(circle_at_80%_25%,rgba(255,255,255,0.07),transparent_12%),radial-gradient(circle_at_45%_75%,rgba(255,255,255,0.06),transparent_15%)]" />

        <div className="mx-auto max-w-[1650px] rounded-[2rem] border border-white/12 bg-[#071521]/70 p-4 shadow-[0_30px_100px_rgba(0,0,0,0.55)] backdrop-blur-md md:p-6">
          <header className="grid gap-4 rounded-[1.6rem] border border-sky-300/20 bg-[linear-gradient(135deg,rgba(10,24,39,0.96),rgba(5,15,28,0.96))] p-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.08)] md:grid-cols-[1fr_auto_1fr] md:items-center md:p-6">
            <div className="flex items-center gap-4">
              <div className="grid h-18 w-18 place-items-center rounded-2xl border border-sky-300/25 bg-sky-400/10 shadow-[0_0_45px_rgba(14,165,233,0.25)]">
                <CloudRain className="h-10 w-10 text-sky-200" />
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.4em] text-sky-200/85">Carbon Intelligence Project</p>
                <h1 className="mt-1 text-4xl font-black uppercase tracking-[0.22em] text-white md:text-5xl">
                  CarbonDrop
                </h1>
                <p className="mt-2 max-w-xl text-sm leading-relaxed text-slate-200/80 md:text-base">
                  AI-powered carbon footprint tracking that turns everyday receipts, trips, and energy use into clear emission insights and actionable reduction plans.
                </p>
              </div>
            </div>

            <div className="flex items-center justify-center md:px-4">
              <div className="rounded-full border border-white/15 bg-white/8 px-5 py-2 text-center text-[0.72rem] font-semibold uppercase tracking-[0.35em] text-slate-100/80">
                Real-time awareness for sustainable decisions
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
              <StatCard value="4+" label="Carbon Modules" tone="cyan" />
              <StatCard value="AI" label="Analysis Pipeline" tone="green" />
              <StatCard value="24/7" label="Budget Tracking" tone="amber" />
            </div>
          </header>

          <main className="mt-4 grid gap-4 lg:grid-cols-12">
            <PosterPanel className="lg:col-span-3">
              <SectionTitle
                eyebrow="Project Overview"
                title="Why CarbonDrop?"
                subtitle="CarbonDrop is designed to make carbon data understandable, visible, and personal. It blends document intelligence, emission-factor mapping, and behavior-aware recommendations into one workflow."
              />
              <div className="space-y-3 text-sm leading-relaxed text-slate-100/80">
                <p>
                  Users upload receipts or activity details, and the platform extracts relevant items, classifies the document, and estimates emissions from trusted datasets.
                </p>
                <p>
                  The result is not just a number. CarbonDrop surfaces the biggest sources of impact, highlights what can be changed, and shows how much difference those changes make.
                </p>
              </div>

              <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
                <div className="rounded-2xl border border-sky-300/15 bg-sky-400/8 p-4">
                  <div className="flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.25em] text-sky-100">
                    <Sparkles className="h-4 w-4" />
                    Core Goal
                  </div>
                  <p className="mt-2 text-sm text-slate-100/75">Help users reduce their footprint through awareness, simulations, and measurable goals.</p>
                </div>
                <div className="rounded-2xl border border-emerald-300/15 bg-emerald-400/8 p-4">
                  <div className="flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.25em] text-emerald-100">
                    <ShieldCheck className="h-4 w-4" />
                    Output
                  </div>
                  <p className="mt-2 text-sm text-slate-100/75">Dashboards, carbon budgets, comparison views, and reduction recommendations.</p>
                </div>
              </div>
            </PosterPanel>

            <PosterPanel className="lg:col-span-6">
              <SectionTitle
                eyebrow="How It Works"
                title="From Receipt to Reduction"
                subtitle="CarbonDrop follows a simple but reliable pipeline: capture data, read the document, estimate emissions, and guide the next decision."
              />

              <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                {processSteps.map((step, index) => (
                  <div key={step.title} className="rounded-2xl border border-white/10 bg-slate-950/45 p-4">
                    <div className="flex items-center justify-between">
                      <div className="grid h-11 w-11 place-items-center rounded-xl border border-sky-300/20 bg-sky-400/10">
                        <step.icon className="h-5 w-5 text-sky-200" />
                      </div>
                      <div className="text-xs font-black uppercase tracking-[0.3em] text-white/35">0{index + 1}</div>
                    </div>
                    <h3 className="mt-3 text-lg font-bold text-white">{step.title}</h3>
                    <p className="mt-2 text-sm leading-relaxed text-slate-100/72">{step.description}</p>
                  </div>
                ))}
              </div>

              <WorkflowArrow />

              <div className="mt-3 grid gap-3 lg:grid-cols-[1.15fr_0.85fr]">
                <div className="rounded-2xl border border-cyan-300/15 bg-[linear-gradient(135deg,rgba(15,23,42,0.95),rgba(8,15,27,0.95))] p-4">
                  <div className="flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.28em] text-cyan-100">
                    <LineChart className="h-4 w-4" />
                    Carbon Flow
                  </div>
                  <div className="mt-4 grid gap-3 sm:grid-cols-5 sm:items-center">
                    {[
                      "Upload",
                      "OCR + Parse",
                      "Emission Engine",
                      "Budget View",
                      "Actions",
                    ].map((label, index) => (
                      <div key={label} className="flex items-center gap-2 sm:block">
                        <div className="rounded-2xl border border-white/10 bg-white/5 px-3 py-4 text-center text-sm font-semibold text-slate-100/85">
                          {label}
                        </div>
                        {index < 4 ? <ArrowRight className="hidden h-4 w-4 text-cyan-200/70 sm:block" /> : null}
                      </div>
                    ))}
                  </div>
                  <p className="mt-4 text-sm leading-relaxed text-slate-100/70">
                    The engine keeps the data path transparent so users can trust where every carbon value comes from.
                  </p>
                </div>

                <div className="rounded-2xl border border-emerald-300/15 bg-emerald-400/8 p-4">
                  <div className="flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.28em] text-emerald-100">
                    <Zap className="h-4 w-4" />
                    Key Outcomes
                  </div>
                  <ul className="mt-4 space-y-3 text-sm leading-relaxed text-slate-100/78">
                    {benefits.map((item) => (
                      <li key={item} className="flex gap-3 rounded-xl border border-white/8 bg-slate-950/35 p-3">
                        <span className="mt-1 h-2.5 w-2.5 rounded-full bg-emerald-300 shadow-[0_0_12px_rgba(110,231,183,0.8)]" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </PosterPanel>

            <PosterPanel className="lg:col-span-3">
              <SectionTitle
                eyebrow="Real Time Applications"
                title="Where It Helps"
                subtitle="CarbonDrop is useful anywhere carbon awareness matters: homes, campuses, teams, and public sustainability programs."
              />
              <div className="space-y-3">
                {applications.map((app) => (
                  <div key={app.title} className="rounded-2xl border border-white/10 bg-slate-950/40 p-3">
                    <div className="flex items-center gap-3">
                      <div className="grid h-11 w-11 shrink-0 place-items-center rounded-xl border border-cyan-300/18 bg-cyan-400/10">
                        <app.icon className="h-5 w-5 text-cyan-200" />
                      </div>
                      <div>
                        <h3 className="text-sm font-bold uppercase tracking-[0.2em] text-white">{app.title}</h3>
                        <p className="mt-1 text-sm leading-relaxed text-slate-100/72">{app.text}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-4 rounded-2xl border border-amber-300/15 bg-amber-400/8 p-4">
                <div className="flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.28em] text-amber-100">
                  <AlertTriangle className="h-4 w-4" />
                  Problem It Solves
                </div>
                <p className="mt-2 text-sm leading-relaxed text-slate-100/76">
                  Most people know sustainability matters, but they do not see the hidden emissions in daily choices. CarbonDrop fills that visibility gap.
                </p>
              </div>
            </PosterPanel>

            <PosterPanel className="lg:col-span-4">
              <SectionTitle
                eyebrow="Carbon Modules"
                title="Tracked Categories"
                subtitle="The platform focuses on the categories most users can act on immediately."
              />
              <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                {moduleCards.map((module) => (
                  <div key={module.title} className="rounded-2xl border border-white/10 bg-slate-950/40 p-3">
                    <div className="flex items-center gap-3">
                      <div className="grid h-10 w-10 place-items-center rounded-xl border border-emerald-300/18 bg-emerald-400/10">
                        <module.icon className="h-5 w-5 text-emerald-200" />
                      </div>
                      <div>
                        <h3 className="text-sm font-bold uppercase tracking-[0.18em] text-white">{module.title}</h3>
                        <p className="mt-1 text-xs leading-relaxed text-slate-100/70">{module.text}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </PosterPanel>

            <PosterPanel className="lg:col-span-4">
              <SectionTitle
                eyebrow="What It Looks Like"
                title="Poster-Level Interface"
                subtitle="CarbonDrop combines dashboard clarity with the precision of a technical poster: compact sections, clear labels, and a visible data pipeline."
              />
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="rounded-2xl border border-white/10 bg-slate-950/45 p-4">
                  <div className="text-xs uppercase tracking-[0.3em] text-sky-200/80">Insight Layer</div>
                  <div className="mt-2 text-2xl font-black text-white">Budget</div>
                  <p className="mt-2 text-sm text-slate-100/72">Daily and monthly emissions stay visible against personal targets.</p>
                </div>
                <div className="rounded-2xl border border-white/10 bg-slate-950/45 p-4">
                  <div className="text-xs uppercase tracking-[0.3em] text-emerald-200/80">Recommendation Layer</div>
                  <div className="mt-2 text-2xl font-black text-white">Act</div>
                  <p className="mt-2 text-sm text-slate-100/72">Suggestions show the next best low-carbon shift, not just the problem.</p>
                </div>
              </div>

              <div className="mt-3 rounded-2xl border border-cyan-300/15 bg-[linear-gradient(135deg,rgba(14,165,233,0.16),rgba(16,185,129,0.08))] p-4">
                <div className="flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.28em] text-cyan-100">
                  <CloudRain className="h-4 w-4" />
                  Design Language
                </div>
                <p className="mt-2 text-sm leading-relaxed text-slate-100/76">
                  Dark storm-blue surfaces, bright emission highlights, and subtle glass panels echo the sample poster while keeping the subject tied to CarbonDrop.
                </p>
              </div>
            </PosterPanel>

            <PosterPanel className="lg:col-span-4">
              <SectionTitle
                eyebrow="Why It Matters"
                title="Impact Summary"
                subtitle="The project is useful because it makes carbon accounting understandable enough for everyday behavior change."
              />

              <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-1">
                <StatCard value="Fast" label="User Feedback Loop" tone="green" />
                <StatCard value="Clear" label="Emission Visibility" tone="cyan" />
                <StatCard value="Smart" label="Behavior Guidance" tone="amber" />
              </div>

              <div className="mt-4 rounded-2xl border border-white/10 bg-slate-950/42 p-4">
                <div className="flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.28em] text-white/85">
                  <Leaf className="h-4 w-4 text-emerald-200" />
                  Closing Statement
                </div>
                <p className="mt-3 text-lg font-semibold leading-relaxed text-slate-50">
                  “When the footprint is visible, the future becomes easier to change.”
                </p>
                <p className="mt-3 text-sm leading-relaxed text-slate-100/70">
                  CarbonDrop helps users see their impact, compare alternatives, and act with confidence.
                </p>
              </div>
            </PosterPanel>
          </main>

          <footer className="mt-4 rounded-[1.4rem] border border-white/10 bg-white/6 p-4">
            <div className="grid gap-3 lg:grid-cols-[1fr_auto_1fr] lg:items-center">
              <div>
                <p className="text-xs uppercase tracking-[0.34em] text-slate-200/60">CarbonDrop Project Poster</p>
                <p className="mt-2 text-sm leading-relaxed text-slate-100/72">
                  Built as a React poster layout for the CarbonDrop project, with modular sections that can be exported as an image for presentation or submission.
                </p>
              </div>

              <div className="hidden h-16 w-px bg-white/10 lg:block" />

              <div className="flex flex-wrap items-center gap-3 lg:justify-end">
                <div className="rounded-full border border-white/12 bg-slate-950/45 px-4 py-2 text-xs font-semibold uppercase tracking-[0.28em] text-slate-100/70">
                  React + Tailwind + Lucide
                </div>
                <div className="rounded-full border border-white/12 bg-slate-950/45 px-4 py-2 text-xs font-semibold uppercase tracking-[0.28em] text-slate-100/70">
                  Landscape poster format
                </div>
              </div>
            </div>
          </footer>
        </div>
      </div>
    </div>
  );
}