# Forcesword

WIP alternative frontend for [SourceForge](https://sourceforge.net/) and other [Apache Allura](https://allura.apache.org/) websites. Built around the [Allura REST API](https://anypoint.mulesoft.com/apiplatform/forge-allura/#/portals/organizations/86c00a85-31e6-4302-b36d-049ca5d042fd/apis/32370/versions/33732) with [Flask](https://flask.palletsprojects.com) and [Bootstrap](https://getbootstrap.com/).

## Todo

Entire site:

- [ ] Login/authentication
- [ ] Home page load faster (prefetch over a set period?)
- [x] Use sqlite3 database for caching user profile icons (instead of pkl file) (kind of, added a lock file to prevent corruption)
- [x] Home page with a list of some projects, etc
- [x] About page

Summary page:

- [ ] Download button / [stats](https://sourceforge.net/p/forge/documentation/Download%20Stats%20API/) (`/projects/<proj>/files/stats/json?start_date=2014-10-29&end_date=2014-11-04`)
- [ ] Sliding navbar instead of wrapping
- [ ] Screenshot modal
- [x] Relative time (i.e., `3 days ago`) for dates/times under 1 month
- [x] Recent Activity ellipse cutoff on one line
- [x] Developer icons in a table instead of a list
- [x] More verbose recent activity pane
- [x] Add metadata (category, license, programming language, operating systems, etc)
- [x] Screenshot carousel

User profile page:

- [x] Better profile image layout / position
- [x] Personal data
- [x] List of projects
- [x] Skills
- [x] Recent activity (may have to resort to rss feed, `/u/<user>/profile/feed.rss`)

Discussion / thread pages:

- [ ] User profile icons
- [ ] Emoji replies (if possible, not shown on API)
- [ ] Block quote markdown support
- [ ] Collapse replies
- [ ] Reply / text input box
- [ ] Vertical lines to align replies (i.e. reddit, hn)
- [ ] Thread metadata (created date, author, forum, last updated)
- [ ] Pagination in both discussion page and thread page
- [ ] Show attachments

New pages:

- [ ] Wiki
- [ ] Bugs
- [ ] News
- [ ] Files (may have to resort to rss feed, `/p/<proj>/rss?path=/<path>`)
- [ ] Code (may have to have backends for different vcs, no idea how to do this, one of the most important parts)
- [x] Discussion

## License

Licensed under the GNU General Public License version 3.

Portions of this project borrowed from [startbootstrap-blog-post](https://github.com/StartBootstrap/startbootstrap-blog-post).

<a href="https://www.flaticon.com/free-icons/sword" title="sword icons">Sword icons created by Freepik - Flaticon</a>