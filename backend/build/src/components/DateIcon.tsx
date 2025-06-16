import { Tooltip } from "@mui/material";
import "../styling/DateIcon.css"

export default function DateIcon({date}: {date:string}) {
    const matchDate = new Date(date);
      const options: Intl.DateTimeFormatOptions = {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    };
    const formattedDate: string = matchDate.toLocaleDateString(undefined, options);
    const splitDate = formattedDate.split(" ")

    return (
        <Tooltip title={formattedDate}>
        <div className="dateCircle">
            <div className="day">{splitDate[0]}</div>
            <div className="month">{splitDate[1]}</div>
        </div>
        </Tooltip>
    )
} 