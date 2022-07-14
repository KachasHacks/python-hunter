from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import os
from dotenv import load_dotenv

load_dotenv()

transport = AIOHTTPTransport(
    "https://salto.stepzen.net/api/guiding-seal/__graphql",
    headers={"Authorization": os.environ.get("KEY")},
)
client = Client(transport=transport, fetch_schema_from_transport=True)


def get_author_from_article(url):
    author_query = gql(
        """
            query getAuther($apiKey: String!, $url: String!) {
            getAuther(api_key: $apiKey , url: $url) {
                data{
                  domain
                  last_name
                  first_name
                  email
                  linkedin_url
                  twitter
                  position
                  company
                  sources {
                    domain
                    extracted_on
                    still_on_page
                    last_seen_on
                  }
                }
              }

            }
            """
    )
    params = {"apiKey": os.environ.get("HUNTERAPIKEY"), "url": url}
    result = client.execute(author_query, variable_values=params)

    return result


def get_emails_from_domain(url):
    domain_query = gql(
        """
        query searchDomain($apiKey: String!, $domain: String!){
          searchDomain(api_key: $apiKey, domain: $domain){
            data{
              domain
              emails {
                value
                linkedin
                last_name
                first_name
                seniority
                type
                confidence
                sources {
                  domain
                  last_seen_on
                  extracted_on
                  still_on_page
                }
              }
            }
          }
        }
        """
    )
    params = {
        "apiKey": os.environ.get("HUNTERAPIKEY"),
        "domain": url,
    }
    result = client.execute(domain_query, variable_values=params)

    return result
