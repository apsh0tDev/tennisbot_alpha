commands_message = f"""🤖 **Commands:**

                    `!live`: Displays a full list of today's live matches and current scores
                    `!schedule`: Displays a list of scheduled events
                    """

#Urls
schedule_url = f"https://sports.ny.betmgm.com/en/sports/api/widget/widgetdata?layoutSize=Large&page=SportLobby&sportId=5&widgetId=/mobilesports-v1.0/layout/layout_standards/modules/sportgrid&shouldIncludePayload=true"
draftkings_url = f"https://sportsbook-nash.draftkings.com/sites/US-SB/api/v4/featured/displaygroups/6/live?format=json"
draftkings_url_scheduled = f"https://sportsbook-nash-usva.draftkings.com/sites/US-VA-SB/api/v2/displaygroupinfo?format=json"

fanduel_url = f"https://sbapi.ny.sportsbook.fanduel.com/api/content-managed-page?page=SPORT&eventTypeId=2&_ak=FhMFpcPWXMeyZxOx&timezone=America%2FNew_York"


proxy_needed = [
    "Draftkings",
    "FanDuel"
]