/** A presentation-only view of the link analytics data. */
export type LinkMetrics = {
  id: string;
  title: string;
  placement: string;
  requests: number;
  transitions: number;
  uniqueDaily: number;
};

type Props = { links: LinkMetrics[]; loading: boolean; error?: string };

export function LinkMetricsTable({ links, loading, error }: Props) {
  if (error) return <p role="alert">{error}</p>;
  if (loading) return <p role="status">Loading link statistics…</p>;
  if (!links.length) return <p>No links found.</p>;

  return (
    <section aria-labelledby="link-metrics-title">
      <h2 id="link-metrics-title">Link statistics</h2>
      <p>Daily unique counts are estimates, not confirmed subscriptions.</p>
      <table>
        <thead><tr>
          <th scope="col">Link</th><th scope="col">Placement</th>
          <th scope="col">Transitions</th><th scope="col">Daily unique ≈</th>
          <th scope="col">Technical requests</th>
        </tr></thead>
        <tbody>{links.map((link) => (
          <tr key={link.id}>
            <th scope="row">{link.title}</th><td>{link.placement || "—"}</td>
            <td>{link.transitions}</td><td>{link.uniqueDaily}</td>
            <td>{link.requests - link.transitions}</td>
          </tr>
        ))}</tbody>
      </table>
    </section>
  );
}
