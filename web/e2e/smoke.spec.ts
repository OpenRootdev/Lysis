import { test, expect } from "@playwright/test";

test("home loads with no console errors", async ({ page }) => {
  const errors: string[] = [];
  page.on("console", (m) => m.type() === "error" && errors.push(m.text()));
  await page.goto("/");
  await expect(page).toHaveTitle(/.+/);
  expect(errors).toEqual([]);
});