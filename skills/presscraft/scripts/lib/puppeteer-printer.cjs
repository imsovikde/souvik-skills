"use strict";

const path = require("path");
const fs = require("fs");

function resolveModule(moduleName) {
  const searchPaths = [
    path.resolve(__dirname, "../../node_modules", moduleName),
    path.resolve(__dirname, "../../../../node_modules", moduleName),
    path.resolve("C:/Users/imsov/.gemini/antigravity/brain/da0cf17a-a5f4-42a2-b2cf-beb070443afc/scratch/node_modules", moduleName)
  ];

  for (const p of searchPaths) {
    if (fs.existsSync(p)) {
      return require(p);
    }
  }
  return require(moduleName);
}

const puppeteer = resolveModule("puppeteer");

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

async function printToPdf(htmlContent, outputPath, options = {}) {
  const browser = await puppeteer.launch({
    headless: "new",
    args: [
      "--no-sandbox",
      "--disable-setuid-sandbox",
      "--font-render-hinting=none",
      "--disable-font-subpixel-positioning"
    ]
  });

  try {
    const page = await browser.newPage();

    // High-DPI viewport setup
    await page.setViewport({
      width: options.landscape ? 1754 : 1240,
      height: options.landscape ? 1240 : 1754,
      deviceScaleFactor: 2
    });

    // Set document content
    await page.setContent(htmlContent, {
      waitUntil: ["networkidle0", "domcontentloaded"],
      timeout: 90000
    });

    // Ensure all web fonts are loaded
    await page.evaluateHandle("document.fonts.ready");

    const waitTime = typeof options.wait === "number" ? options.wait : 600;
    if (waitTime > 0) {
      await new Promise((resolve) => setTimeout(resolve, waitTime));
    }

    // Configure margins
    let margin = {
      top: "18mm",
      right: "16mm",
      bottom: "20mm",
      left: "16mm"
    };

    if (typeof options.margin === "string") {
      margin = {
        top: options.margin,
        right: options.margin,
        bottom: options.margin,
        left: options.margin
      };
    } else if (typeof options.margin === "object" && options.margin !== null) {
      margin = Object.assign(margin, options.margin);
    }

    const showHeaderFooter = options.headerFooter !== false;
    const docTitle = options.title ? escapeHtml(options.title) : "";
    const docAuthor = options.author ? escapeHtml(options.author) : "";

    const headerTemplate = options.headerTemplate || `
      <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 8pt; width: 100%; display: flex; justify-content: space-between; padding: 0 16mm; color: #888888; box-sizing: border-box;">
        <span>${docTitle}</span>
        <span></span>
      </div>
    `;

    const footerTemplate = options.footerTemplate || `
      <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 8pt; width: 100%; display: flex; justify-content: space-between; padding: 0 16mm; color: #888888; box-sizing: border-box;">
        <span>${docAuthor}</span>
        <span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>
      </div>
    `;

    const pdfOptions = {
      path: outputPath,
      format: options.format || "A4",
      landscape: Boolean(options.landscape),
      printBackground: true,
      scale: 1.0, // Strict scale 1.0, never shrink
      preferCSSPageSize: true,
      displayHeaderFooter: showHeaderFooter,
      headerTemplate: showHeaderFooter ? headerTemplate : "<div></div>",
      footerTemplate: showHeaderFooter ? footerTemplate : "<div></div>",
      margin
    };

    await page.pdf(pdfOptions);

    const stats = fs.statSync(outputPath);
    return {
      success: true,
      outputPath: path.resolve(outputPath),
      bytes: stats.size
    };
  } finally {
    await browser.close();
  }
}

module.exports = {
  printToPdf
};
