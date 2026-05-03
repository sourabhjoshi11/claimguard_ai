import { useEffect, useMemo, useState } from "react";
import { fetchClaims, loginUser, registerUser, uploadClaim } from "./api";
import { downloadClaimReportPdf } from "./reportPdf";

const STORAGE_KEY = "claimguard-auth";
const ANALYSIS_STEPS = [
  "Files received",
  "Reference check complete",
  "Visual comparison running",
  "Damage summary prepared",
  "Report ready",
];

const initialAuthState = {
  username: "",
  access: "",
  refresh: "",
};

function loadStoredAuth() {
  try {
    const storedValue = window.localStorage.getItem(STORAGE_KEY);
    if (!storedValue) {
      return initialAuthState;
    }
    return { ...initialAuthState, ...JSON.parse(storedValue) };
  } catch (error) {
    return initialAuthState;
  }
}

function formatCurrency(value) {
  if (typeof value !== "number") {
    return "Not available";
  }

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(value);
}

function buildReportData(workflowResult, username, claimId, mediaType) {
  if (!workflowResult) {
    return null;
  }

  return {
    claimId,
    analyst: username,
    createdAt: new Date().toLocaleString(),
    status: workflowResult.status || "Processing finished",
    mediaType,
    totalClaimValue:
      typeof workflowResult.total_claim_value === "number"
        ? workflowResult.total_claim_value
        : null,
    issues: Array.isArray(workflowResult.anamolies) ? workflowResult.anamolies : [],
  };
}

function getSeverityTone(severity) {
  const value = String(severity || "").toLowerCase();
  if (value === "high") {
    return "high";
  }
  if (value === "medium") {
    return "medium";
  }
  return "low";
}

function App() {
  const [authMode, setAuthMode] = useState("login");
  const [auth, setAuth] = useState(loadStoredAuth);
  const [authForm, setAuthForm] = useState({ username: "", email: "", password: "" });
  const [claims, setClaims] = useState([]);
  const [mediaType, setMediaType] = useState("image");
  const [incidentFile, setIncidentFile] = useState(null);
  const [referenceFile, setReferenceFile] = useState(null);
  const [incidentPreview, setIncidentPreview] = useState("");
  const [referencePreview, setReferencePreview] = useState("");
  const [status, setStatus] = useState("");
  const [isAuthSubmitting, setIsAuthSubmitting] = useState(false);
  const [isLoadingClaims, setIsLoadingClaims] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisStep, setAnalysisStep] = useState(0);
  const [latestResponse, setLatestResponse] = useState(null);

  const isAuthenticated = Boolean(auth.access);
  const acceptedMedia = mediaType === "video" ? "video/*" : "image/*";
  const report = useMemo(
    () =>
      buildReportData(
        latestResponse?.workflow_result || null,
        auth.username || "Claim specialist",
        latestResponse?.claim_id || null,
        latestResponse?.media_type || mediaType,
      ),
    [auth.username, latestResponse, mediaType],
  );
  const damageCount = report?.issues?.length || 0;
  const activeStep = isAnalyzing ? analysisStep : report ? ANALYSIS_STEPS.length - 1 : -1;

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(auth));
  }, [auth]);

  useEffect(() => {
    if (!incidentFile) {
      setIncidentPreview("");
      return undefined;
    }

    const url = URL.createObjectURL(incidentFile);
    setIncidentPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [incidentFile]);

  useEffect(() => {
    if (!referenceFile) {
      setReferencePreview("");
      return undefined;
    }

    const url = URL.createObjectURL(referenceFile);
    setReferencePreview(url);
    return () => URL.revokeObjectURL(url);
  }, [referenceFile]);

  useEffect(() => {
    if (!auth.access) {
      setClaims([]);
      return;
    }

    let isMounted = true;
    setIsLoadingClaims(true);

    fetchClaims(auth.access)
      .then((response) => {
        if (isMounted) {
          setClaims(response.claims || []);
        }
      })
      .catch((error) => {
        if (isMounted) {
          setStatus(error.message);
        }
      })
      .finally(() => {
        if (isMounted) {
          setIsLoadingClaims(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [auth.access]);

  useEffect(() => {
    if (!isAnalyzing) {
      setAnalysisStep(0);
      return undefined;
    }

    const interval = window.setInterval(() => {
      setAnalysisStep((current) =>
        current >= ANALYSIS_STEPS.length - 1 ? current : current + 1,
      );
    }, 950);

    return () => window.clearInterval(interval);
  }, [isAnalyzing]);

  function updateAuthForm(event) {
    const { name, value } = event.target;
    setAuthForm((current) => ({ ...current, [name]: value }));
  }

  async function handleAuthSubmit(event) {
    event.preventDefault();
    setIsAuthSubmitting(true);
    setStatus("");

    try {
      if (authMode === "register") {
        await registerUser(authForm);
      }

      const tokens = await loginUser(authForm);
      setAuth({
        username: authForm.username || authForm.email,
        access: tokens.access,
        refresh: tokens.refresh,
      });
      setAuthForm({ username: "", email: "", password: "" });
      setStatus("Workspace ready.");
    } catch (error) {
      setStatus(error.message);
    } finally {
      setIsAuthSubmitting(false);
    }
  }

  async function handleUploadSubmit(event) {
    event.preventDefault();

    if (!incidentFile || !referenceFile) {
      setStatus("Upload both the reference file and the current evidence file.");
      return;
    }

    setStatus("Claim analysis started.");
    setIsAnalyzing(true);
    setLatestResponse(null);

    try {
      const response = await uploadClaim(auth.access, incidentFile, referenceFile, mediaType);
      setLatestResponse(response);
      setClaims((current) => [
        {
          id: response.claim_id,
          image_url: response.image_url,
          status: response.workflow_result?.status || "uploaded",
        },
        ...current,
      ]);

      if (typeof response.workflow_result?.total_claim_value === "number") {
        setStatus(
          `Report ready. Estimated damage cost: ${formatCurrency(
            response.workflow_result.total_claim_value,
          )}.`,
        );
      } else {
        setStatus(response.workflow_result?.status || "Analysis completed.");
      }
    } catch (error) {
      setStatus(error.message);
    } finally {
      setIsAnalyzing(false);
    }
  }

  function handleLogout() {
    setAuth(initialAuthState);
    setClaims([]);
    setIncidentFile(null);
    setReferenceFile(null);
    setLatestResponse(null);
    setStatus("Signed out.");
  }

  function handleDownloadReport() {
    if (report) {
      downloadClaimReportPdf(report);
    }
  }

  function clearSelection() {
    setReferenceFile(null);
    setIncidentFile(null);
    setLatestResponse(null);
    setStatus("");
  }

  function renderPreview(label, file, previewUrl) {
    const isVideo = mediaType === "video";

    return (
      <article className="preview-card">
        <div className="preview-head">
          <div>
            <span className="eyebrow">{label}</span>
            <h3>{file ? file.name : "No file selected"}</h3>
          </div>
          <span className="chip">{isVideo ? "Video" : "Image"}</span>
        </div>
        <div className="preview-frame">
          {previewUrl && !isVideo ? (
            <img alt={`${label} preview`} src={previewUrl} />
          ) : (
            <div className="placeholder">
              <strong>{file ? "Ready to analyze" : "Waiting for upload"}</strong>
              <p>
                {isVideo
                  ? "Video frames are prepared during processing."
                  : "A preview appears here after file selection."}
              </p>
            </div>
          )}
        </div>
      </article>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="page auth-page">
        <main className="auth-layout">
          <section className="auth-copy">
            <span className="eyebrow">ClaimGuard AI</span>
            <h1>Simple claim comparison workspace for before and after evidence.</h1>
            <p>
              Upload two files, run the comparison, and review the claim summary in one
              clean screen.
            </p>
            <div className="mini-stats">
              <article>
                <strong>2-file workflow</strong>
                <span>Reference plus current evidence</span>
              </article>
              <article>
                <strong>Image or video</strong>
                <span>Same intake flow for both</span>
              </article>
              <article>
                <strong>Structured report</strong>
                <span>Damages, estimate, and export</span>
              </article>
            </div>
          </section>

          <section className="auth-panel">
            <div className="toggle">
              <button
                className={authMode === "login" ? "toggle-button active" : "toggle-button"}
                onClick={() => setAuthMode("login")}
                type="button"
              >
                Sign in
              </button>
              <button
                className={authMode === "register" ? "toggle-button active" : "toggle-button"}
                onClick={() => setAuthMode("register")}
                type="button"
              >
                Register
              </button>
            </div>

            <div className="panel-copy">
              <h2>{authMode === "login" ? "Open workspace" : "Create account"}</h2>
              <p>Use your account to upload claim evidence and review past runs.</p>
            </div>

            <form className="stack" onSubmit={handleAuthSubmit}>
              {authMode === "register" ? (
                <label className="field">
                  <span>Username</span>
                  <input
                    name="username"
                    onChange={updateAuthForm}
                    placeholder="case.manager"
                    required
                    value={authForm.username}
                  />
                </label>
              ) : null}
              <label className="field">
                <span>{authMode === "login" ? "Email or username" : "Email"}</span>
                <input
                  name="email"
                  onChange={updateAuthForm}
                  placeholder={
                    authMode === "login" ? "name@company.com or case.manager" : "name@company.com"
                  }
                  required
                  type={authMode === "login" ? "text" : "email"}
                  value={authForm.email}
                />
              </label>
              <label className="field">
                <span>Password</span>
                <input
                  name="password"
                  onChange={updateAuthForm}
                  placeholder="Enter password"
                  required
                  type="password"
                  value={authForm.password}
                />
              </label>
              <button className="primary-button" disabled={isAuthSubmitting} type="submit">
                {isAuthSubmitting
                  ? "Working..."
                  : authMode === "login"
                    ? "Enter workspace"
                    : "Create and continue"}
              </button>
            </form>

            {status ? <p className="status-message">{status}</p> : null}
          </section>
        </main>
      </div>
    );
  }

  return (
    <div className="page">
      <header className="topbar">
        <div>
          <span className="eyebrow">ClaimGuard AI</span>
          <h1>Claim comparison desk</h1>
          <p>Review reference and incident evidence with a cleaner workflow.</p>
        </div>
        <div className="topbar-side">
          <div className="user-card">
            <strong>{auth.username || "Analyst"}</strong>
            <span>{isAnalyzing ? "Analysis in progress" : "Ready for review"}</span>
          </div>
          <button className="secondary-button" onClick={handleLogout} type="button">
            Sign out
          </button>
        </div>
      </header>

      <main className="dashboard">
        <section className="hero-card">
          <div className="hero-copy-block">
            <span className="eyebrow">Current run</span>
            <h2>Upload the before and after files, then let the model flag visible damage.</h2>
            <p>
              The interface stays simple on purpose: pick the media type, attach both
              files, and review the findings and estimate once processing finishes.
            </p>
          </div>
          <div className="hero-metrics">
            <article>
              <span>Claims</span>
              <strong>{isLoadingClaims ? "..." : claims.length}</strong>
            </article>
            <article>
              <span>Damage items</span>
              <strong>{damageCount}</strong>
            </article>
            <article>
              <span>Estimate</span>
              <strong>{formatCurrency(report?.totalClaimValue)}</strong>
            </article>
          </div>
        </section>

        <section className="content-grid">
          <section className="panel upload-panel">
            <div className="panel-head">
              <div>
                <span className="eyebrow">Upload</span>
                <h2>Evidence intake</h2>
              </div>
              <div className="toggle compact">
                <button
                  className={mediaType === "image" ? "toggle-button active" : "toggle-button"}
                  onClick={() => setMediaType("image")}
                  type="button"
                >
                  Image
                </button>
                <button
                  className={mediaType === "video" ? "toggle-button active" : "toggle-button"}
                  onClick={() => setMediaType("video")}
                  type="button"
                >
                  Video
                </button>
              </div>
            </div>

            <form className="stack" onSubmit={handleUploadSubmit}>
              <label className="file-field">
                <span>Reference file</span>
                <input
                  accept={acceptedMedia}
                  onChange={(event) => setReferenceFile(event.target.files?.[0] || null)}
                  type="file"
                />
                <strong>{referenceFile ? referenceFile.name : `Choose the before ${mediaType}`}</strong>
                <small>Baseline media used for comparison.</small>
              </label>

              <label className="file-field">
                <span>Incident file</span>
                <input
                  accept={acceptedMedia}
                  onChange={(event) => setIncidentFile(event.target.files?.[0] || null)}
                  type="file"
                />
                <strong>{incidentFile ? incidentFile.name : `Choose the after ${mediaType}`}</strong>
                <small>Current evidence to analyze for damage.</small>
              </label>

              <div className="action-row">
                <button className="primary-button" disabled={isAnalyzing} type="submit">
                  {isAnalyzing ? "Analyzing..." : "Run analysis"}
                </button>
                <button className="secondary-button" onClick={clearSelection} type="button">
                  Clear
                </button>
              </div>
            </form>

            {status ? <p className="status-message">{status}</p> : null}

            <div className="preview-grid">
              {renderPreview("Reference", referenceFile, referencePreview)}
              {renderPreview("Incident", incidentFile, incidentPreview)}
            </div>
          </section>

          <section className="side-column">
            <section className="panel">
              <div className="panel-head">
                <div>
                  <span className="eyebrow">Progress</span>
                  <h2>Workflow status</h2>
                </div>
                <span className={`status-pill ${isAnalyzing ? "live" : report ? "done" : ""}`}>
                  {isAnalyzing ? "Running" : report ? "Complete" : "Idle"}
                </span>
              </div>

              <div className="progress-list">
                {ANALYSIS_STEPS.map((step, index) => {
                  const state =
                    index < activeStep ? "done" : index === activeStep ? "active" : "idle";

                  return (
                    <article className={`progress-item ${state}`} key={step}>
                      <span className="progress-dot" />
                      <div>
                        <strong>{step}</strong>
                        <p>
                          {state === "done"
                            ? "Complete"
                            : state === "active"
                              ? "In progress"
                              : "Waiting"}
                        </p>
                      </div>
                    </article>
                  );
                })}
              </div>
            </section>

            <section className="panel">
              <div className="panel-head">
                <div>
                  <span className="eyebrow">History</span>
                  <h2>Recent claims</h2>
                </div>
                <span className="muted-copy">
                  {isLoadingClaims ? "Refreshing..." : `${claims.length} total`}
                </span>
              </div>

              <div className="history-list">
                {claims.length ? (
                  claims.map((claim) => (
                    <article className="history-item" key={claim.id}>
                      <div>
                        <strong>Claim #{claim.id}</strong>
                        <p>{claim.status}</p>
                      </div>
                      <a href={claim.image_url} rel="noreferrer" target="_blank">
                        Open
                      </a>
                    </article>
                  ))
                ) : (
                  <div className="empty-state">
                    <strong>No uploads yet</strong>
                    <p>Your processed claims will appear here.</p>
                  </div>
                )}
              </div>
            </section>
          </section>
        </section>

        <section className="results-grid">
          <section className="panel">
            <div className="panel-head">
              <div>
                <span className="eyebrow">Summary</span>
                <h2>Claim report</h2>
              </div>
              <button
                className="primary-button"
                disabled={!report}
                onClick={handleDownloadReport}
                type="button"
              >
                Export PDF
              </button>
            </div>

            {report ? (
              <div className="summary-grid">
                <article className="summary-card">
                  <span>Claim ID</span>
                  <strong>{report.claimId || "Pending"}</strong>
                </article>
                <article className="summary-card">
                  <span>Analyst</span>
                  <strong>{report.analyst}</strong>
                </article>
                <article className="summary-card">
                  <span>Media type</span>
                  <strong>{report.mediaType}</strong>
                </article>
                <article className="summary-card">
                  <span>Total estimate</span>
                  <strong>{formatCurrency(report.totalClaimValue)}</strong>
                </article>
                <article className="summary-card wide">
                  <span>Status</span>
                  <strong>{report.status}</strong>
                </article>
              </div>
            ) : (
              <div className="empty-state large">
                <strong>No report available</strong>
                <p>Run an analysis to generate the summary and exportable PDF.</p>
              </div>
            )}
          </section>

          <section className="panel">
            <div className="panel-head">
              <div>
                <span className="eyebrow">Findings</span>
                <h2>Detected damage</h2>
              </div>
              <span className="muted-copy">{damageCount} items</span>
            </div>

            {report?.issues?.length ? (
              <div className="finding-list">
                {report.issues.map((issue, index) => (
                  <article className="finding-item" key={`${issue.item || "issue"}-${index}`}>
                    <div className="finding-meta">
                      <strong>{issue.item || "Damage item"}</strong>
                      <span className={`severity-pill ${getSeverityTone(issue.severity)}`}>
                        {issue.severity || "Low"}
                      </span>
                    </div>
                    <p>{issue.issue || "No description provided."}</p>
                    <strong className="finding-cost">
                      {formatCurrency(issue.estimated_cost)}
                    </strong>
                  </article>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <strong>No detailed findings yet</strong>
                <p>Damage items will show up here after a completed comparison.</p>
              </div>
            )}
          </section>
        </section>
      </main>
    </div>
  );
}

export default App;
