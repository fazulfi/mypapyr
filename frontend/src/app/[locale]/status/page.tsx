import { isLocale, type Locale } from "@/lib/i18n";
import { getMessages } from "@/lib/messages";
import { AdSlot } from "@/components/ads/AdSlot";
import {
  resolveSupportingPageCopy,
  type SupportingPageCopy,
  type SupportingPageProps,
} from "@/components/supporting-page";
import {
  DEFAULT_THRESHOLDS,
  EMPTY_SNAPSHOTS,
  deriveStatus,
  type GlobalAvailability,
  type RegionLevel,
  type StatusSnapshot,
  type StatusThresholds,
} from "@/lib/status";

// OP-02 status surface: state accent panels and region dots use Tailwind
// default-theme tokens (emerald = operational, amber = degraded, rose = down,
// slate = unknown), matching the support-color language in design-tokens.ts.

const STATE_PANEL: Record<GlobalAvailability, string> = {
  operational: "border-emerald-200 bg-emerald-50",
  degraded: "border-amber-200 bg-amber-50",
  down: "border-rose-200 bg-rose-50",
  unknown: "border-slate-200 bg-white",
};

const STATE_DOT: Record<GlobalAvailability, string> = {
  operational: "bg-emerald-500",
  degraded: "bg-amber-500",
  down: "bg-rose-500",
  unknown: "bg-slate-400",
};

const REGION_DOT: Record<RegionLevel, string> = {
  operational: "bg-emerald-500",
  degraded: "bg-amber-500",
  down: "bg-rose-500",
};

function formatObservedAt(observedAt: number, locale: Locale): string {
  return new Date(observedAt).toLocaleString(locale);
}

/**
 * OP-02 status page content. A server component: derives an observed-
 * availability label from approved snapshots (branch default: the empty safe
 * input) and never fetches the VPS, /health, or any API endpoint.
 */
export function StatusContent({
  locale,
  copy,
  snapshots = EMPTY_SNAPSHOTS,
  thresholds = DEFAULT_THRESHOLDS,
}: {
  locale: string;
  copy: SupportingPageCopy;
  snapshots?: readonly StatusSnapshot[];
  thresholds?: StatusThresholds;
}): React.ReactElement {
  const validLocale = isLocale(locale) ? locale : "en";
  const status = getMessages(validLocale).statusPage;
  const derived = deriveStatus(snapshots, thresholds);
  const policy = status.policyBody
    .replace("{failures}", String(thresholds.consecutiveFailures))
    .replace("{regions}", String(thresholds.downRegions));
  const lastObserved =
    derived.observedAt !== null ? (
      <time dateTime={new Date(derived.observedAt).toISOString()}>
        {formatObservedAt(derived.observedAt, validLocale)}
      </time>
    ) : (
      status.neverObserved
    );

  return (
    <div className="mx-auto w-full max-w-2xl px-4 py-12 sm:py-16">
      <h1 className="text-2xl font-bold text-navy sm:text-3xl">{copy.title}</h1>
      <p className="mt-3 text-[15px] text-slate-500">{copy.description}</p>
      <p className="mt-3 text-[15px] text-slate-500">{status.observedDisclaimer}</p>

      <div className={`mt-8 rounded-xl border p-6 ${STATE_PANEL[derived.state]}`}>
        <div className="flex items-center gap-3">
          <span
            aria-hidden="true"
            className={`h-2.5 w-2.5 rounded-full ${STATE_DOT[derived.state]}`}
          />
          <h2 className="text-lg font-semibold text-navy">{status.state[derived.state]}</h2>
        </div>
        <p className="mt-2 text-[15px] leading-relaxed text-slate-600">
          {status.stateBody[derived.state]}
        </p>
        {derived.sufficient ? null : (
          <p className="mt-2 text-[13px] text-slate-500">{status.insufficientNote}</p>
        )}
        <p className="mt-3 text-[13px] text-slate-500">
          {status.lastObservedLabel}: {lastObserved}
        </p>
      </div>

      {derived.regions.length > 0 ? (
        <section className="mt-10" aria-labelledby="status-regions-heading">
          <h2 id="status-regions-heading" className="text-lg font-semibold text-navy">
            {status.regionsHeading}
          </h2>
          <ul className="mt-3 divide-y divide-slate-200 rounded-xl border border-slate-200 bg-white">
            {derived.regions.map((region) => (
              <li key={region.region} className="flex items-center justify-between gap-4 px-5 py-3">
                <span className="text-[15px] font-medium text-navy">{region.region}</span>
                <span className="flex items-center gap-2 text-[13px] text-slate-500">
                  <span
                    aria-hidden="true"
                    className={`h-2 w-2 rounded-full ${REGION_DOT[region.level]}`}
                  />
                  {status.regionState[region.level]}
                  {region.consecutiveFailures > 0 ? ` (${region.consecutiveFailures})` : null}
                </span>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      <div className="mt-10 rounded-xl bg-slate-100 p-6">
        <h2 className="text-base font-semibold text-navy">{status.policyHeading}</h2>
        <p className="mt-2 text-[14px] leading-relaxed text-slate-600">{policy}</p>
      </div>

      <div
        className="mt-10 flex max-w-full flex-col items-center gap-6 overflow-hidden"
        aria-label={copy.adLabel}
      >
        <AdSlot pageSlug="status" immediate unit="banner-468x60" label={copy.adLabel} />
      </div>
    </div>
  );
}

export default async function StatusPage({
  params,
}: SupportingPageProps): Promise<React.ReactElement> {
  const { locale } = await params;
  const copy = await resolveSupportingPageCopy(params, "status");
  return <StatusContent locale={locale} copy={copy} />;
}
