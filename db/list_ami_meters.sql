WITH CTE AS (
    SELECT
        tc.turnout_id,
        MAX(tmr.ReadingDate) AS reading_date
    FROM
        turnoutcodes tc
    LEFT JOIN
        TabletMeterReadings tmr
        ON tc.Turnout_ID = tmr.Turnout_ID
    WHERE
        tc.code_id = '{ami_code}'
    GROUP BY
        tc.Turnout_ID
)
SELECT
    CTE.Turnout_ID,
    CTE.reading_date,
    tmr.Odometer,
	t.Description as descrip,
	lat.LatName as lateral
FROM
    CTE
JOIN
    TabletMeterReadings tmr ON CTE.Turnout_ID = tmr.Turnout_ID
    AND CTE.reading_date = tmr.ReadingDate
join
	turnout t on cte.Turnout_ID = t.Turnout_ID
left join latTurnout lt on t.Turnout_ID = lt.turnout_id
left join lat on lt.latid = lat.id
ORDER BY
    CTE.Turnout_ID;
