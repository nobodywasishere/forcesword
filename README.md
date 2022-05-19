# Forcesword

WIP alternative frontend for [SourceForge](https://sourceforge.net/) and other [Apache Allura](https://allura.apache.org/) websites. Built around the [Allura REST API](https://anypoint.mulesoft.com/apiplatform/forge-allura/#/portals/organizations/86c00a85-31e6-4302-b36d-049ca5d042fd/apis/32370/versions/33732) with [Flask](https://flask.palletsprojects.com) and [Bootstrap](https://getbootstrap.com/).

## Todo

Entire site:

- [ ] Login/authentication
- [ ] Home page with a list of some projects, etc
- [ ] About page

Summary page:

- [ ] Developer icons in a table instead of a list
- [ ] More verbose recent activity pane
- [ ] Add metadata (category, license, programming language, operating systems, etc)
- [ ] Download button / [stats](https://sourceforge.net/p/forge/documentation/Download%20Stats%20API/) (`/projects/<proj>/files/stats/json?start_date=2014-10-29&end_date=2014-11-04`)

User profile page:

- [ ] Personal data
- [ ] List of projects
- [ ] Skills
- [ ] Recent activity (may have to resort to rss feed, `/u/<user>/profile/feed.rss`)

New pages:

- [ ] Wiki
- [ ] Discussion
- [ ] Bugs
- [ ] News
- [ ] Files (may have to resort to rss feed, `/p/<proj>/rss?path=/<path>`)
- [ ] Code (may have to have backends for different vcs, no idea how to do this, one of the most important parts)

## License

Licensed under the GNU General Public License version 3.

Portions of this project borrowed from [startbootstrap-blog-post](https://github.com/StartBootstrap/startbootstrap-blog-post).

<a href="https://www.flaticon.com/free-icons/sword" title="sword icons">Sword icons created by Freepik - Flaticon</a>