import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";

import type { DispatchDetails } from "./types";

const formatDate = (value?: string | null) => {
  if (!value) return "-";
  return new Date(value).toLocaleDateString("en-GB");
};

export const generateDispatchChallanPdf = (dispatch: DispatchDetails) => {
  const doc = new jsPDF({
    orientation: "portrait",
    unit: "mm",
    format: "a4",
  });

  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();

  /* ===========================================================
      COMPANY HEADER
  =========================================================== */

  doc.setFillColor(25, 52, 100);
  doc.rect(0, 0, pageWidth, 28, "F");

  doc.setTextColor(255, 255, 255);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(18);
  doc.text("GEE BEE NETWORK PRIVATE LIMITED", pageWidth / 2, 10, {
    align: "center",
  });

  doc.setFontSize(9);
  doc.setFont("helvetica", "normal");

  doc.text(
    "NAISS, INS Rajali, Arakkonam",
    pageWidth / 2,
    16,
    { align: "center" }
  );

  doc.text(
    "Email: project.rajali@gbnetwork.co.in | Phone: +91-9591959085",
    pageWidth / 2,
    22,
    { align: "center" }
  );

  /* ===========================================================
      TITLE
  =========================================================== */

  doc.setTextColor(0, 0, 0);

  doc.setDrawColor(60);
  doc.setFillColor(235, 240, 248);
  doc.roundedRect(14, 34, pageWidth - 28, 12, 2, 2, "FD");

  doc.setFontSize(18);
  doc.setFont("helvetica", "bold");
  doc.text("DELIVERY CHALLAN", pageWidth / 2, 42, {
    align: "center",
  });

  /* ===========================================================
      DISPATCH DETAILS
  =========================================================== */

  let y = 55;

  doc.setFontSize(10);

  doc.roundedRect(14, y, pageWidth - 28, 36, 2, 2);

  const left = 18;
  const right = 110;

  doc.setFont("helvetica", "bold");
  doc.text("Dispatch No", left, y + 8);
  doc.text("Challan No", left, y + 15);
  doc.text("Dispatch Date", left, y + 22);
  doc.text("Purpose", left, y + 29);

  doc.text("Vendor", right, y + 8);
  doc.text("Courier", right, y + 15);
  doc.text("Tracking No", right, y + 22);
  doc.text("Status", right, y + 29);

  doc.setFont("helvetica", "normal");

  doc.text(dispatch.dispatch_no || "-", left + 32, y + 8);
  doc.text(dispatch.delivery_challan_no || "-", left + 32, y + 15);
  doc.text(formatDate(dispatch.dispatch_date), left + 32, y + 22);
  doc.text(dispatch.purpose || "-", left + 32, y + 29);

  doc.text(dispatch.vendor_name || "-", right + 24, y + 8);
  doc.text(dispatch.courier_name || "-", right + 24, y + 15);
  doc.text(dispatch.tracking_number || "-", right + 24, y + 22);
  doc.text(dispatch.status || "-", right + 24, y + 29);

  y += 45;

  /* ===========================================================
      REMARKS
  =========================================================== */

  if (dispatch.remarks) {
    doc.setFont("helvetica", "bold");
    doc.text("Remarks", 14, y);

    doc.setFont("helvetica", "normal");

    const remarks = doc.splitTextToSize(
      dispatch.remarks,
      pageWidth - 34
    );

    doc.roundedRect(
      14,
      y + 3,
      pageWidth - 28,
      remarks.length * 5 + 6,
      2,
      2
    );

    doc.text(remarks, 18, y + 8);

    y += remarks.length * 5 + 14;
  }

  /* ===========================================================
      ITEMS TABLE
  =========================================================== */

  autoTable(doc, {
    startY: y,

    head: [
      [
        "Sl",
        "Type",
        "Asset / Component",
        "Category",
        "Serial Number",
        "Qty",
        "Status",
      ],
    ],

    body: dispatch.items.map((item, index) => [
      index + 1,

      item.dispatch_type,

      item.dispatch_type === "Asset"
        ? item.asset_number || "-"
        : item.component_name || "-",

      item.asset_category || item.asset_subcategory || "-",

      item.asset_serial_number || "-",

      item.quantity,

      item.status,
    ]),

    theme: "grid",

    headStyles: {
      fillColor: [25, 52, 100],
      textColor: 255,
      halign: "center",
      fontStyle: "bold",
      fontSize: 10,
    },

    bodyStyles: {
      fontSize: 9,
      valign: "middle",
    },

    alternateRowStyles: {
      fillColor: [245, 245, 245],
    },

    styles: {
      lineWidth: 0.2,
      cellPadding: 2,
    },

    margin: {
      left: 14,
      right: 14,
    },
  });

  let finalY = (doc as any).lastAutoTable.finalY + 10;

  /* ===========================================================
      SUMMARY
  =========================================================== */

  doc.setFillColor(245, 245, 245);

  doc.roundedRect(14, finalY, pageWidth - 28, 18, 2, 2, "FD");

  doc.setFont("helvetica", "bold");

  doc.text(
    `Total Items : ${dispatch.items.length}`,
    18,
    finalY + 7
  );

  doc.text(
    `Total Quantity : ${dispatch.items.reduce(
      (a, b) => a + b.quantity,
      0
    )}`,
    18,
    finalY + 14
  );

  finalY += 28;

  /* ===========================================================
      SIGNATURES
  =========================================================== */

  const boxWidth = 55;

  [
    "Prepared By",
    "Verified By",
    "Vendor Representative",
  ].forEach((title, i) => {
    const x = 14 + i * 62;

    doc.roundedRect(x, finalY, boxWidth, 28, 2, 2);

    doc.setFont("helvetica", "bold");

    doc.text(title, x + boxWidth / 2, finalY + 23, {
      align: "center",
    });
  });

  /* ===========================================================
      FOOTER
  =========================================================== */

  const totalPages = doc.getNumberOfPages();

  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i);

    doc.setFontSize(8);

    doc.setTextColor(120);

    doc.text(
      `Generated from SIRMS | ${new Date().toLocaleString()}`,
      14,
      pageHeight - 8
    );

    doc.text(
      `Page ${i} of ${totalPages}`,
      pageWidth - 14,
      pageHeight - 8,
      {
        align: "right",
      }
    );
  }

  doc.save(
    `Delivery_Challan_${dispatch.dispatch_no || dispatch.id}.pdf`
  );
};