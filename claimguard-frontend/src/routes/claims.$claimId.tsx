import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { ArrowLeft, AlertCircle, CheckCircle2, FileImage } from "lucide-react";
import { Header } from "@/components/Header";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/lib/auth-context";
import { api, resolveMediaUrl, type Claim, type WorkflowResult } from "@/lib/api";
import { toast } from "sonner";

export const Route = createFileRoute("/claims/$claimId")({
  component: ClaimDetailPage,
  head: () => ({ meta: [{ title: "Claim — ClaimGuard AI" }] }),
});

function severityColor(sev: string) {
  const s = sev.toLowerCase();
  if (s === "high") return "bg-destructive/10 text-destructive border-destructive/30";
  if (s === "medium") return "bg-warning/15 text-foreground border-warning/40";
  return "bg-success/15 text-foreground border-success/40";
}

function ClaimDetailPage() {
  const { claimId } = Route.useParams();
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [claim, setClaim] = useState<(Claim & { workflow_result?: WorkflowResult }) | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate({ to: "/login" });
      return;
    }
    api
      .getClaim(claimId)
      .then(setClaim)
      .catch((err) => toast.error(err instanceof Error ? err.message : "Failed to load claim"))
      .finally(() => setLoading(false));
  }, [claimId, isAuthenticated, navigate]);

  const wf = claim?.workflow_result;

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto max-w-4xl px-4 py-10">
        <Link to="/claims" className="mb-6 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4" /> Back to claims
        </Link>

        {loading ? (
          <div className="h-64 animate-pulse rounded-xl bg-muted/60" />
        ) : !claim ? (
          <Card className="p-10 text-center text-muted-foreground">Claim not found.</Card>
        ) : (
          <>
            <div className="flex items-end justify-between">
              <div>
                <h1 className="text-3xl font-semibold tracking-tight text-foreground">
                  Claim #{claim.id}
                </h1>
                {claim.created_at && (
                  <p className="mt-1 text-sm text-muted-foreground">
                    Submitted {new Date(claim.created_at).toLocaleString()}
                  </p>
                )}
              </div>
              <Badge variant="secondary">{claim.status}</Badge>
            </div>

            <Card className="mt-6 overflow-hidden border-border/60 shadow-[var(--shadow-card)]">
              <div className="aspect-video w-full bg-muted">
                {claim.image_url ? (
                  <img src={resolveMediaUrl(claim.image_url)} alt={`Claim ${claim.id}`} className="h-full w-full object-cover" />
                ) : (
                  <div className="flex h-full items-center justify-center text-muted-foreground">
                    <FileImage className="h-10 w-10" />
                  </div>
                )}
              </div>
            </Card>

            {wf && (
              <Card className="mt-6 overflow-hidden border-border/60 shadow-[var(--shadow-card)]">
                <div className="border-b border-border bg-[image:var(--gradient-subtle)] p-6">
                  <div className="flex items-center gap-2">
                    {wf.status.toLowerCase().includes("complete") ? (
                      <CheckCircle2 className="h-5 w-5 text-success" />
                    ) : (
                      <AlertCircle className="h-5 w-5 text-warning" />
                    )}
                    <h2 className="text-lg font-semibold">Workflow result</h2>
                    <Badge variant="secondary" className="ml-auto">{wf.status}</Badge>
                  </div>
                  <div className="mt-4 grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs uppercase tracking-wider text-muted-foreground">Anomalies</p>
                      <p className="mt-1 text-lg font-semibold text-foreground">{wf.anamolies.length}</p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-wider text-muted-foreground">Total estimate</p>
                      <p className="mt-1 text-lg font-semibold text-primary">
                        ${wf.total_claim_value.toFixed(2)}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="p-6">
                  <h3 className="mb-3 text-sm font-medium text-muted-foreground">Detected anomalies</h3>
                  {wf.anamolies.length === 0 ? (
                    <p className="text-sm text-muted-foreground">No anomalies were detected.</p>
                  ) : (
                    <div className="space-y-2">
                      {wf.anamolies.map((a, i) => (
                        <div key={i} className="flex items-start justify-between gap-3 rounded-lg border border-border bg-card p-4">
                          <div className="flex-1">
                            <p className="font-medium text-foreground">{a.item}</p>
                            <p className="mt-0.5 text-sm text-muted-foreground">{a.issue}</p>
                          </div>
                          <div className="flex flex-col items-end gap-2">
                            <span className={`rounded-full border px-2.5 py-0.5 text-xs font-medium ${severityColor(a.severity)}`}>
                              {a.severity}
                            </span>
                            {typeof a.estimated_cost === "number" && (
                              <span className="text-sm font-semibold text-foreground">
                                ${a.estimated_cost.toFixed(2)}
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </Card>
            )}
          </>
        )}
      </main>
    </div>
  );
}
