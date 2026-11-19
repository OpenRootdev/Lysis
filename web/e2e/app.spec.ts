import { test, expect, type Page } from "@playwright/test";

const issue = {
  number: 42,
  full_title: "Fix typo in README",
  url: "https://github.com/psf/requests/issues/42",
  score: 0.8,
  why: "Small, well-scoped change.",
};

async function mockApi(page: Page, rank: { status: number; body: unknown }) {
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
  await page.route(/\/rank\?/, (r) =>
    r.fulfill({ status: rank.status, json: rank.body }),
  );
  await page.route(/\/feedback$/, (r) => r.fulfill({ status: 201, json: { saved: true } }));
}

async function search(page: Page, value: string) {
  const input = page.getByLabel("Repository, owner/repo");
  await input.fill(value);
  await input.press("Enter");
}

test("ranks issues from a mocked API", async ({ page }) => {
  await mockApi(page, {
    status: 200,
    body: { repo: "psf/requests", model_date: "2026-01-01", issues: [issue] },
  });
  await page.goto("/");
  await search(page, "psf/requests");
  await expect(page.getByRole("link", { name: "Fix typo in README" })).toBeVisible();
  await expect(page.getByText("Small, well-scoped change.")).toBeVisible();
});

test("rejects invalid input without calling the API", async ({ page }) => {
  let called = false;
  await mockApi(page, { status: 200, body: {} });
  await page.route(/\/rank\?/, (r) => {
    called = true;
    return r.fulfill({ status: 200, json: {} });
  });
  await page.goto("/");
  await search(page, "not a repo");
  await expect(page.getByRole("alert")).toBeVisible();
  expect(called).toBe(false);
});

test("shows an error on 429", async ({ page }) => {
  await mockApi(page, {
    status: 429,
    body: { detail: "The service is busy, try again in a few minutes." },
  });
  await page.goto("/");
  await search(page, "psf/requests");
  await expect(page.locator('p[role="alert"]')).toContainText("Rate limit reached");
});

test("voting locks the buttons and says thanks", async ({ page }) => {
  await mockApi(page, {
    status: 200,
    body: { repo: "psf/requests", model_date: "2026-01-01", issues: [issue] },
  });
  await page.goto("/");
  await search(page, "psf/requests");
  await page.getByRole("button", { name: "Yes" }).click();
  await expect(page.getByText("thanks")).toBeVisible();
  await expect(page.getByRole("button", { name: "Yes" })).toBeDisabled();
});