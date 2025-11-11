import { notFound } from "next/navigation";

import { MatchControlPanel } from "@/components/admin/match-control-panel";
import { getApiClient } from "@/lib/api/server";

type AdminMatchPageProps = {
  params: Promise<{ matchId: string }>;
};

export default async function AdminMatchPage({ params }: AdminMatchPageProps) {
  const { matchId } = await params;
  const api = getApiClient();

  let match;
  try {
    match = await api.getMatch(matchId);
  } catch {
    notFound();
  }

  const [homeTeam, awayTeam] = await Promise.all([
    api.getTeam(match.home.teamId),
    api.getTeam(match.away.teamId),
  ]);

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-4 py-10 sm:px-6 lg:px-8">
      <MatchControlPanel match={match} homeTeam={homeTeam} awayTeam={awayTeam} />
    </div>
  );
}

