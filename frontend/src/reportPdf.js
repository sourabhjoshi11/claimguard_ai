function escapePdfText(value) {
  return String(value)
    .replaceAll("\\", "\\\\")
    .replaceAll("(", "\\(")
    .replaceAll(")", "\\)");
}

function wrapText(text, maxLength = 82) {
  const words = String(text || "").split(/\s+/).filter(Boolean);
  const lines = [];
  let current = "";

  words.forEach((word) => {
    const candidate = current ? `${current} ${word}` : word;
    if (candidate.length > maxLength) {
      if (current) {
        lines.push(current);
      }
      current = word;
    } else {
      current = candidate;
    }
  });

  if (current) {
    lines.push(current);
  }

  return lines.length ? lines : [""];
}

export function downloadClaimReportPdf(report) {
  const lines = [
    "ClaimGuard AI Damage Report",
    "",
    `Claim ID: ${report.claimId || "Pending"}`,
    `Prepared by: ${report.analyst || "Unknown"}`,
    `Created at: ${report.createdAt || ""}`,
    `Status: ${report.status || "Unknown"}`,
    `Estimated total: ${
      typeof report.totalClaimValue === "number"
        ? `$${report.totalClaimValue.toFixed(2)}`
        : "Not available"
    }`,
    "",
    "Damage Findings:",
  ];

  if (report.issues?.length) {
    report.issues.forEach((issue, index) => {
      lines.push(
        `${index + 1}. ${issue.item || "Damage item"} | ${issue.severity || "Unknown"} | ${
          typeof issue.estimated_cost === "number"
            ? `$${issue.estimated_cost.toFixed(2)}`
            : "No cost"
        }`,
      );
      wrapText(issue.issue || "No description provided").forEach((line) => {
        lines.push(`   ${line}`);
      });
      lines.push("");
    });
  } else {
    lines.push("No detailed damage findings returned.");
  }

  const textCommands = [];
  let y = 780;

  lines.forEach((line) => {
    const wrapped = wrapText(line);
    wrapped.forEach((wrappedLine) => {
      textCommands.push(`1 0 0 1 50 ${y} Tm (${escapePdfText(wrappedLine)}) Tj`);
      y -= 18;
    });
  });

  const content = `BT\n/F1 12 Tf\n${textCommands.join("\n")}\nET`;
  const objects = [
    "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj",
    "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj",
    "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj",
    "4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj",
    `5 0 obj << /Length ${content.length} >> stream\n${content}\nendstream endobj`,
  ];

  let pdf = "%PDF-1.4\n";
  const offsets = [0];

  objects.forEach((object) => {
    offsets.push(pdf.length);
    pdf += `${object}\n`;
  });

  const xrefStart = pdf.length;
  pdf += `xref\n0 ${objects.length + 1}\n`;
  pdf += "0000000000 65535 f \n";
  offsets.slice(1).forEach((offset) => {
    pdf += `${String(offset).padStart(10, "0")} 00000 n \n`;
  });
  pdf += `trailer << /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefStart}\n%%EOF`;

  const blob = new Blob([pdf], { type: "application/pdf" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `claim-report-${report.claimId || "draft"}.pdf`;
  anchor.click();
  URL.revokeObjectURL(url);
}
