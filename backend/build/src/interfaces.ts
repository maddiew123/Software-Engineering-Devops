export type Match = {
    match_id?: number;
    location: string;
    date: string;
    opponent_team_id: number;
    home_team_id: number;
    match_report: string;
  };

export type Team = {
        team_id?: number
        team_name: string;
    };