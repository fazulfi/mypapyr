import { describe, expect, it } from "vitest";

import { getMessages, messages } from "../messages";
import { locales } from "../i18n";

type JsonTree = { [key: string]: string | JsonTree };

function collectKeys(node: JsonTree, prefix = ""): string[] {
  return Object.entries(node).flatMap(([key, value]) => {
    const path = prefix ? `${prefix}.${key}` : key;
    if (typeof value === "string") {
      return [path];
    }
    return collectKeys(value, path);
  });
}

describe("SH-01 message resources", () => {
  it("defines the same message key structure in every locale", () => {
    const keys = collectKeys(messages.en as unknown as JsonTree);
    expect(keys.length).toBeGreaterThan(0);
    for (const locale of locales) {
      expect(collectKeys(messages[locale] as unknown as JsonTree)).toEqual(keys);
    }
  });

  it("has no empty or whitespace-only message values", () => {
    for (const locale of locales) {
      for (const value of collectKeys(messages[locale] as unknown as JsonTree).map((key) =>
        key.split(".").reduce<string | JsonTree>(
          (node, part) => {
            const next = (node as JsonTree)[part];
            return typeof next === "string" ? next : next;
          },
          messages[locale] as unknown as JsonTree,
        ),
      )) {
        expect(typeof value).toBe("string");
        expect((value as string).trim()).not.toBe("");
      }
    }
  });

  it("keeps native language names invariant across locales", () => {
    for (const locale of locales) {
      expect(messages[locale].languages.en).toBe("English");
      expect(messages[locale].languages.es).toBe("Español");
      expect(messages[locale].languages.id).toBe("Bahasa Indonesia");
    }
  });

  it("keeps the brand name identical in every locale", () => {
    for (const locale of locales) {
      expect(messages[locale].siteName).toBe("Papyr");
    }
  });

  it("translates shell and home copy per locale", () => {
    expect(messages.es.nav.home).not.toBe(messages.en.nav.home);
    expect(messages.id.nav.home).not.toBe(messages.en.nav.home);
    expect(messages.es.home.description).not.toBe(messages.en.home.description);
    expect(messages.id.home.description).not.toBe(messages.en.home.description);
  });

  it("returns the resource for the requested locale", () => {
    expect(getMessages("es")).toBe(messages.es);
    expect(getMessages("id")).toBe(messages.id);
  });
});

describe("SH-03 accessibility and metadata copy", () => {
  it("defines skip-to-content and metadata keys in every locale", () => {
    for (const locale of locales) {
      const copy = messages[locale];
      expect(copy.a11y.skipToContent.trim()).not.toBe("");
      expect(copy.metadata.title.trim()).not.toBe("");
      expect(copy.metadata.description.trim()).not.toBe("");
    }
  });

  it("localizes the skip-to-content label per locale", () => {
    const en = messages.en.a11y.skipToContent;
    expect(messages.es.a11y.skipToContent).not.toBe(en);
    expect(messages.id.a11y.skipToContent).not.toBe(en);
  });

  it("localizes the metadata title and description per locale", () => {
    const enTitle = messages.en.metadata.title;
    const enDescription = messages.en.metadata.description;
    expect(messages.es.metadata.title).not.toBe(enTitle);
    expect(messages.id.metadata.title).not.toBe(enTitle);
    expect(messages.es.metadata.description).not.toBe(enDescription);
    expect(messages.id.metadata.description).not.toBe(enDescription);
  });

  it("keeps metadata copy free of unproven speed, privacy, and free claims", () => {
    const claimPattern = /free|fast|instant|secure|private|privacy/i;
    for (const locale of locales) {
      expect(messages[locale].metadata.title).not.toMatch(claimPattern);
      expect(messages[locale].metadata.description).not.toMatch(claimPattern);
    }
  });
});

describe("SH-05 notFound and navigation copy", () => {
  it("defines notFound title and description in every locale", () => {
    for (const locale of locales) {
      expect(messages[locale].notFound.title.trim()).not.toBe("");
      expect(messages[locale].notFound.description.trim()).not.toBe("");
    }
  });

  it("localizes notFound copy per locale", () => {
    const enTitle = messages.en.notFound.title;
    const enDescription = messages.en.notFound.description;
    expect(messages.es.notFound.title).not.toBe(enTitle);
    expect(messages.id.notFound.title).not.toBe(enTitle);
    expect(messages.es.notFound.description).not.toBe(enDescription);
    expect(messages.id.notFound.description).not.toBe(enDescription);
  });

  it("defines nav category labels in every locale", () => {
    for (const locale of locales) {
      expect(messages[locale].nav.basic.trim()).not.toBe("");
      expect(messages[locale].nav.conversion.trim()).not.toBe("");
    }
  });

  it("localizes nav category labels per locale", () => {
    const enBasic = messages.en.nav.basic;
    const enConversion = messages.en.nav.conversion;
    expect(messages.es.nav.basic).not.toBe(enBasic);
    expect(messages.id.nav.basic).not.toBe(enBasic);
    expect(messages.es.nav.conversion).not.toBe(enConversion);
    expect(messages.id.nav.conversion).not.toBe(enConversion);
  });

  it("defines nav menu and CTA controls in every locale", () => {
    for (const locale of locales) {
      expect(messages[locale].nav.menu.trim()).not.toBe("");
      expect(messages[locale].nav.menuClose.trim()).not.toBe("");
      expect(messages[locale].nav.cta.trim()).not.toBe("");
    }
  });

  it("localizes nav menu and CTA controls per locale", () => {
    const enMenu = messages.en.nav.menu;
    const enMenuClose = messages.en.nav.menuClose;
    const enCta = messages.en.nav.cta;
    expect(messages.es.nav.menu).not.toBe(enMenu);
    expect(messages.id.nav.menu).not.toBe(enMenu);
    expect(messages.es.nav.menuClose).not.toBe(enMenuClose);
    expect(messages.id.nav.menuClose).not.toBe(enMenuClose);
    expect(messages.es.nav.cta).not.toBe(enCta);
    expect(messages.id.nav.cta).not.toBe(enCta);
  });

  it("defines additional a11y controls in every locale", () => {
    for (const locale of locales) {
      expect(messages[locale].a11y.languageSwitcher.trim()).not.toBe("");
      expect(messages[locale].a11y.navToggle.trim()).not.toBe("");
      expect(messages[locale].a11y.navClose.trim()).not.toBe("");
    }
  });

  it("localizes additional a11y controls per locale", () => {
    const enLangSwitcher = messages.en.a11y.languageSwitcher;
    const enNavToggle = messages.en.a11y.navToggle;
    const enNavClose = messages.en.a11y.navClose;
    expect(messages.es.a11y.languageSwitcher).not.toBe(enLangSwitcher);
    expect(messages.id.a11y.languageSwitcher).not.toBe(enLangSwitcher);
    expect(messages.es.a11y.navToggle).not.toBe(enNavToggle);
    expect(messages.id.a11y.navToggle).not.toBe(enNavToggle);
    expect(messages.es.a11y.navClose).not.toBe(enNavClose);
    expect(messages.id.a11y.navClose).not.toBe(enNavClose);
  });

  it("keeps notFound and nav copy free of TODO/TBD placeholders", () => {
    const placeholderRe = /\bTODO\b|\bTBD\b|#\s*placeholder|\bTK\b|\bFIXME\b/i;
    for (const locale of locales) {
      const copy = messages[locale];
      for (const val of [
        copy.notFound.title,
        copy.notFound.description,
        copy.nav.basic,
        copy.nav.conversion,
        copy.nav.menu,
        copy.nav.menuClose,
        copy.nav.cta,
        copy.a11y.languageSwitcher,
        copy.a11y.navToggle,
        copy.a11y.navClose,
      ]) {
        expect(val).not.toMatch(placeholderRe);
      }
    }
  });
});

describe("SH-06 footer copy", () => {
  const footerRoutes = [
    "privacy",
    "terms",
    "cookiesAdvertising",
    "contact",
    "status",
    "roadmap",
    "blog",
  ] as const;

  it("defines footer section headings and copyright in every locale", () => {
    for (const locale of locales) {
      expect(messages[locale].footer.tools.trim()).not.toBe("");
      expect(messages[locale].footer.support.trim()).not.toBe("");
      expect(messages[locale].footer.copyright.trim()).not.toBe("");
    }
  });

  it("defines all seven support route labels in the footer", () => {
    for (const locale of locales) {
      for (const route of footerRoutes) {
        expect(messages[locale].footer[route].trim()).not.toBe("");
      }
    }
  });

  it("localizes footer section headings per locale", () => {
    const enTools = messages.en.footer.tools;
    const enSupport = messages.en.footer.support;
    expect(messages.es.footer.tools).not.toBe(enTools);
    expect(messages.id.footer.tools).not.toBe(enTools);
    expect(messages.es.footer.support).not.toBe(enSupport);
    expect(messages.id.footer.support).not.toBe(enSupport);
  });

  it("localizes footer support route labels per locale", () => {
    for (const route of footerRoutes) {
      const en = messages.en.footer[route];
      expect(messages.es.footer[route]).not.toBe(en);
      expect(messages.id.footer[route]).not.toBe(en);
    }
  });

  it("keeps footer copy free of TODO/TBD placeholders", () => {
    const placeholderRe = /\bTODO\b|\bTBD\b|#\s*placeholder|\bTK\b|\bFIXME\b/i;
    for (const locale of locales) {
      const f = messages[locale].footer;
      for (const val of [f.tools, f.support, f.copyright, ...footerRoutes.map((r) => f[r])]) {
        expect(val).not.toMatch(placeholderRe);
      }
    }
  });
});

describe("SH-07 homepage sections copy", () => {
  const toolSlugs = ["compress", "merge", "split", "jpgToPdf", "pdfToJpg"] as const;

  it("defines homepage hero and tool directory headings in every locale", () => {
    for (const locale of locales) {
      const h = messages[locale].home;
      expect(h.hero.trim()).not.toBe("");
      expect(h.heroSub.trim()).not.toBe("");
      expect(h.toolsHeading.trim()).not.toBe("");
      for (const slug of toolSlugs) {
        expect(h.tools[slug].trim()).not.toBe("");
      }
    }
  });

  it("localizes homepage hero copy per locale", () => {
    const enHero = messages.en.home.hero;
    const enHeroSub = messages.en.home.heroSub;
    expect(messages.es.home.hero).not.toBe(enHero);
    expect(messages.id.home.hero).not.toBe(enHero);
    expect(messages.es.home.heroSub).not.toBe(enHeroSub);
    expect(messages.id.home.heroSub).not.toBe(enHeroSub);
  });

  it("localizes tool directory headings per locale", () => {
    for (const slug of toolSlugs) {
      const en = messages.en.home.tools[slug];
      expect(messages.es.home.tools[slug]).not.toBe(en);
      expect(messages.id.home.tools[slug]).not.toBe(en);
    }
  });

  it("defines homepage privacy section copy in every locale", () => {
    for (const locale of locales) {
      const h = messages[locale].home;
      expect(h.privacy.trim()).not.toBe("");
      expect(h.privacyDesc.trim()).not.toBe("");
    }
  });

  it("localizes homepage privacy section copy per locale", () => {
    const enPrivacy = messages.en.home.privacy;
    const enPrivacyDesc = messages.en.home.privacyDesc;
    expect(messages.es.home.privacy).not.toBe(enPrivacy);
    expect(messages.id.home.privacy).not.toBe(enPrivacy);
    expect(messages.es.home.privacyDesc).not.toBe(enPrivacyDesc);
    expect(messages.id.home.privacyDesc).not.toBe(enPrivacyDesc);
  });

  it("defines how-it-works and FAQ section headings in every locale", () => {
    for (const locale of locales) {
      expect(messages[locale].home.howItWorks.trim()).not.toBe("");
      expect(messages[locale].home.faq.trim()).not.toBe("");
    }
  });

  it("defines how-it-works steps in every locale", () => {
    for (const locale of locales) {
      const steps = messages[locale].home.howItWorksSteps;
      expect(steps.length).toBeGreaterThan(0);
      for (const step of steps) {
        expect(step.trim()).not.toBe("");
      }
    }
  });

  it("defines FAQ items in every locale", () => {
    for (const locale of locales) {
      const items = messages[locale].home.faqItems;
      expect(items.length).toBeGreaterThan(0);
      for (const item of items) {
        expect(item.question.trim()).not.toBe("");
        expect(item.answer.trim()).not.toBe("");
      }
    }
  });

  it("keeps homepage hero copy free of unproven speed, no-tracking, and no-personal-data claims", () => {
    const forbiddenRe =
      /\b(fast|instant|speedy|lightning|no.tracking|no.personal.data|never.track|never.share)\b/i;
    for (const locale of locales) {
      const h = messages[locale].home;
      for (const val of [
        h.hero,
        h.heroSub,
        h.privacy,
        h.privacyDesc,
        ...h.howItWorksSteps,
        ...h.faqItems.flatMap((item) => [item.question, item.answer]),
      ]) {
        expect(val).not.toMatch(forbiddenRe);
      }
    }
  });

  it("allows only supported factual claims in homepage copy", () => {
    // Supported claims: free, no account, one-hour automatic deletion
    const unsupportedRe =
      /\b(no.personal.data|never.track|tracking.free|no.data.collected|never.share|instant|guaranteed|always|unlimited)\b/i;
    for (const locale of locales) {
      const h = messages[locale].home;
      for (const val of [
        h.hero,
        h.heroSub,
        h.privacy,
        h.privacyDesc,
        ...h.howItWorksSteps,
        ...h.faqItems.flatMap((item) => [item.question, item.answer]),
      ]) {
        expect(val).not.toMatch(unsupportedRe);
      }
    }
  });

  it("keeps homepage copy free of TODO/TBD placeholders", () => {
    const placeholderRe = /\bTODO\b|\bTBD\b|#\s*placeholder|\bTK\b|\bFIXME\b/i;
    for (const locale of locales) {
      const h = messages[locale].home;
      for (const val of [
        h.hero,
        h.heroSub,
        h.toolsHeading,
        ...toolSlugs.map((s) => h.tools[s]),
        h.privacy,
        h.privacyDesc,
        h.howItWorks,
        ...h.howItWorksSteps,
        h.faq,
        ...h.faqItems.flatMap((item) => [item.question, item.answer]),
      ]) {
        expect(val).not.toMatch(placeholderRe);
      }
    }
  });
});
