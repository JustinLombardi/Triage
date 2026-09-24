const META = {
  flaky: { label: "Flaky test", color: "var(--accent-flaky)" },
  infra: { label: "Infrastructure", color: "var(--accent-infra)" },
  bug: { label: "Real bug", color: "var(--accent-bug)" },
  config: { label: "Config or dependency", color: "var(--accent-config)" },
  unknown: { label: "Unclear", color: "var(--accent-unknown)" },
};

export function categoryMeta(category) {
  return META[category] || META.unknown;
}

export default function CategoryBadge({ category, confidence }) {
  const meta = categoryMeta(category);
  return (
    <span style={{ "--cat-color": meta.color }}>
      <span className="badge">
        <span className="dot" />
        {meta.label}
      </span>
      {typeof confidence === "number" && (
        <span className="confidence">
          <span className="meter">
            <span className="meter-fill" style={{ width: `${confidence}%` }} />
          </span>
          {confidence}%
        </span>
      )}
    </span>
  );
}
