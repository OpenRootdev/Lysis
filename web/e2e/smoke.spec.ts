import { test, expect } from "@playwright/test";

test("home loads with no console errors", async ({ page }) => {
  const errors: string[] = [];
  page.on("console", (m) => m.type() === "error" && errors.push(m.text()));

  await page.route(/supabase\.co/, (r) => r.fulfill({ status: 200, body: "[]" }));
  await page.route(/\/model$/, (r) =>
    r.fulfill({
      json: { trained_at: "2026-01-01T00:00:00", n_train: 1000, cv: { ap: 0.5, auc: 0.7 } },
    }),
  );
  await page.route(/\/repos\/meta/, (r) =>
    r.fulfill({
      json: { model_date: "2026-01-01", languages: [], levels: ["beginner", "intermediate", "advanced"] },
    }),
  );
  await page.route(/\/repos\?/, (r) =>
    r.fulfill({ json: { model_date: "2026-01-01", total: 0, repos: [] } }),
  );

  await page.goto("/");
  await expect(page).toHaveTitle(/.+/);
  expect(errors).toEqual([]);
});