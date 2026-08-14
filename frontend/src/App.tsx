import { Activity, FileSearch, ShieldCheck, UploadCloud } from 'lucide-react'

const workflowItems = [
  {
    label: 'Secure Access',
    status: 'Day 2',
    icon: ShieldCheck
  },
  {
    label: 'Case Intake',
    status: 'Day 5',
    icon: UploadCloud
  },
  {
    label: 'Candidate Review',
    status: 'Day 5',
    icon: FileSearch
  },
  {
    label: 'AI Reports',
    status: 'Day 6',
    icon: Activity
  }
]

export function App() {
  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">PehchaanAI</p>
          <h1>Investigation Workspace</h1>
        </div>

        <nav aria-label="Primary navigation">
          <a href="/" aria-current="page">Dashboard</a>
          <a href="/cases">Cases</a>
          <a href="/search">Search</a>
          <a href="/reports">Reports</a>
        </nav>
      </aside>

      <section className="content">
        <header className="topbar">
          <div>
            <p className="eyebrow">MVP Sprint</p>
            <h2>Authentication and backend foundation</h2>
          </div>
          <span className="status-pill">Day 2</span>
        </header>

        <section className="workflow-grid" aria-label="Project workflow">
          {workflowItems.map(({ label, status, icon: Icon }) => (
            <article className="workflow-card" key={label}>
              <Icon aria-hidden="true" size={22} />
              <div>
                <h3>{label}</h3>
                <p>{status}</p>
              </div>
            </article>
          ))}
        </section>

        <section className="panel">
          <div>
            <p className="eyebrow">Backend</p>
            <h3>FastAPI auth API ready for integration</h3>
            <p>
              The frontend will call the backend for registration, login, and
              the current investigator profile before case intake is added.
            </p>
          </div>
          <code>GET /health</code>
        </section>
      </section>
    </main>
  )
}
