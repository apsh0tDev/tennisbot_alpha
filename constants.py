commands_message = f"""🤖 **Commands:**

                    `!live`: Displays a full list of today's live matches and current scores
                    `!schedule`: Displays a list of scheduled events
                    """

#Urls
draftkings_url_scheduled = f"https://sportsbook-nash-usva.draftkings.com/sites/US-VA-SB/api/v2/displaygroupinfo?format=json"



proxy_needed = [
    "Draftkings",
    "FanDuel"
]

#   caller urls
# BetMGM
schedule_url = f"https://sports.ny.betmgm.com/en/sports/api/widget/widgetdata?layoutSize=Large&page=SportLobby&sportId=5&widgetId=/mobilesports-v1.0/layout/layout_standards/modules/sportgrid&shouldIncludePayload=true"
schedule_event = "https://sports.ny.betmgm.com/cds-api/bettingoffer/fixture-view?x-bwin-accessid=ZjVlNTEzYzAtMGUwNC00YTk1LTg4OGYtZDQ4ZGNhOWY4Mjc1&lang=en-us&country=US&userCountry=US&subdivision=US-XY&offerMapping=All&fixtureIds={id}&state=Latest&includePrecreatedBetBuilder=true&supportVirtual=false&isBettingInsightsEnabled=true&useRegionalisedConfiguration=true&includeRelatedFixtures=false&statisticsModes=All"

# FanDuel
fanduel_url = f"https://sbapi.ny.sportsbook.fanduel.com/api/content-managed-page?page=SPORT&eventTypeId=2&_ak=FhMFpcPWXMeyZxOx&timezone=America%2FNew_York"
fanduel_event_url = "https://sbapi.ny.sportsbook.fanduel.com/api/event-page?_ak=FhMFpcPWXMeyZxOx&eventId={id}&tab=all&useCombinedTouchdownsVirtualMarket=true&usePulse=true&useQuickBets=true"

#Draftkings
draftkings_url = f"https://sportsbook-nash.draftkings.com/sites/US-SB/api/v4/featured/displaygroups/6/live?format=json"
draftkings_tournaments = "https://sportsbook-nash-usva.draftkings.com/sites/US-VA-SB/api/v5/eventgroups/{id}?format=json"