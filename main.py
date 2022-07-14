import flet
import os
from dotenv import load_dotenv
from flet import (
    Page,
    Column,
    FloatingActionButton,
    Icon,
    ListView,
    VerticalDivider,
    NavigationRail,
    NavigationRailDestination,
    PopupMenuButton,
    PopupMenuItem,
    Card,
    ListTile,
    Container,
    Row,
    Text,
    AppBar,
    colors,
    ProgressRing,
    icons,
    TextField,
    UserControl,
)

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

from graphql_queries import get_author_from_article, get_emails_from_domain

load_dotenv()

transport = AIOHTTPTransport(
    "https://salto.stepzen.net/api/guiding-seal/__graphql",
    headers={"Authorization": os.environ.get("KEY")},
)
client = Client(transport=transport, fetch_schema_from_transport=True)


class ResultRow(UserControl):
    def __init__(self, title, detail, icon):
        super().__init__()
        self.title = title
        self.detail = detail
        self.icon = icon

    def build(self):

        return Card(
            content=Container(
                content=Column(
                    [
                        ListTile(
                            leading=Icon(self.icon),
                            title=Text(self.detail),
                            subtitle=Text(self.title),
                        )
                    ]
                )
            )
        )


class AuthorSearch(UserControl):
    def build(self):
        self.url_field = TextField(hint_text="Enter url of article", expand=True)
        self.results_view = Column()

        return Column(
            width=600,
            controls=[
                Row(
                    [Text(value="Search for article author", style="headlineMedium")],
                    alignment="center",
                ),
                Row(
                    controls=[
                        self.url_field,
                        FloatingActionButton(
                            icon=icons.SEARCH, on_click=self.search_author
                        ),
                    ],
                ),
                self.results_view,
            ],
        )

    def search_author(self, e):
        row = Row([ProgressRing(), Text("Searching...")], alignment="center")
        self.results_view.controls.append(row)
        self.update()
        result = get_author_from_article(self.url_field.value)
        print(result)
        print(type(result))
        self.url_field.value = ""
        self.results_view.controls.remove(row)
        self.results_view.controls.append(
            ResultRow(
                "Author",
                f'{result["getAuther"]["data"]["first_name"]} {result["getAuther"]["data"]["last_name"]}',
                icons.BOOK_OUTLINED,
            )
        )
        self.results_view.controls.append(
            ResultRow("Email", result["getAuther"]["data"]["email"], icons.MAIL_OUTLINE)
        )
        self.results_view.controls.append(
            ResultRow(
                "Domain", result["getAuther"]["data"]["domain"], icons.WEB_OUTLINED
            )
        )
        self.results_view.controls.append(
            ResultRow(
                "Twitter",
                f'@{result["getAuther"]["data"]["twitter"]}',
                icons.FAVORITE_OUTLINE,
            )
        )
        self.results_view.controls.append(
            ResultRow(
                "LinkedIn",
                result["getAuther"]["data"]["linkedin_url"],
                icons.MAIL_OUTLINE,
            )
        )

        self.update()


class OtherSearch(UserControl):
    def build(self):
        pass


class DomainSearch(UserControl):
    def build(self):
        self.url_field = TextField(hint_text="Enter website url", expand=True)
        self.results_view = Column(scroll="auto", height=400)

        return Column(
            width=600,
            controls=[
                Row(
                    [Text(value="Search Domain for Email", style="headlineMedium")],
                    alignment="center",
                ),
                Row(
                    controls=[
                        self.url_field,
                        FloatingActionButton(
                            icon=icons.SEARCH, on_click=self.search_domain
                        ),
                    ],
                ),
                self.results_view,
            ],
        )

    def search_domain(self, _):
        row = Row([ProgressRing(), Text("Searching...")], alignment="center")
        self.results_view.controls.append(row)
        self.update()
        # result = client.execute(self.domain_query, variable_values=params)
        result = get_emails_from_domain(self.url_field.value)
        print(result)
        self.url_field.value = ""
        self.results_view.controls.remove(row)
        for email in result["searchDomain"]["data"]["emails"]:
            self.results_view.controls.append(
                ResultRow("Email", email["value"], icons.EMAIL_OUTLINED)
            )

        # self.results_view.controls.append(lv)
        # self.results_view.controls.append(
        # ResultRow(
        # "Author",
        # f'{result["getAuther"]["data"]["first_name"]} {result["getAuther"]["data"]["last_name"]}',
        # icons.BOOK_OUTLINED,
        # )
        # )
        self.update()


def main(page: Page):

    page.title = "Hunter"
    page.horizontal_alignment = "center"

    page.appbar = AppBar(
        # leading=Icon(icons.EMAIL),
        # leading_width=40,
        title=Text("Email Hunter"),
        center_title=True,
        color=colors.WHITE,
        bgcolor=colors.PRIMARY,
        actions=[
            PopupMenuButton(
                items=[
                    PopupMenuItem(text="Item 1"),
                    PopupMenuItem(),  # divider
                    PopupMenuItem(text="Checked item"),
                ]
            ),
        ],
    )

    page.update()

    author_search = AuthorSearch()
    domain_search = DomainSearch()

    routes = {"0": author_search, "1": domain_search, "2": Text("Third route")}

    def body_update(e):
        body.controls.clear()
        body.controls.append(routes[str(e.control.selected_index)])
        page.update()

    rail = NavigationRail(
        selected_index=0,
        label_type="all",
        min_width=100,
        min_extended_width=400,
        group_alignment=-0.9,
        destinations=[
            NavigationRailDestination(
                icon=icons.BOOK_OUTLINED,
                selected_icon=icons.BOOK,
                label="Author Search",
            ),
            NavigationRailDestination(
                icon_content=Icon(icons.WEB_OUTLINED),
                selected_icon_content=Icon(icons.WEB),
                label="Domain Search",
            ),
            NavigationRailDestination(
                icon=icons.SETTINGS_OUTLINED,
                selected_icon_content=Icon(icons.SETTINGS),
                label_content=Text("Other Searches"),
            ),
        ],
        on_change=body_update,
    )

    body = Column()
    page.add(Row([rail, VerticalDivider(width=1), body], expand=True))
    body.controls.append(author_search)
    page.update()


flet.app(target=main)
