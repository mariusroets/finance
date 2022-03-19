from .models import Regex
from .dbmanager import Connection
from .tags import Tags

class Regex(Connection):
    """Handles all regex queries"""

    def regex_list(self, with_tags=True, tags_compressed=True):
        """A list of all regexs"""
        if with_tags:
            query = (
                self.session.query(Regex, Tag)
                .join(Regex.tags)
            )
            result = self.query_pd(query)
            result.columns = ['regex_id', 'regex_name', 'tag_id', 'tag_name', 'tag_description']
        else:
            query = self.session.query(Regex)
            result = self.query_pd(query)
            result.columns = ['regex_id', 'regex_name']

        if not with_tags:
            return result

        if tags_compressed:
            result = (
                result
                .groupby('regex_name')
                .tag_name.agg([('count', 'count'), ('tag_name', ', '.join)])
            )

        return result

    def add_regex(self, regex):
        """Adds a regex definition"""
        regex = self.regex_exists(regex_name)
        if regex:
            return regex

        regex = Regex(name=regex_name)
        self.session.add(regex)
        self.session.commit()

        return regex

    def link_regex_tag(self, tag_names, regex_names):
        """Links the given tag to a regex

        :tag_name: TODO
        :regex_id: TODO
        :returns: TODO

        """
        tman = Tags()
        for reg in regex_names:
            regex = self.add_regex(reg)
            for t in tag_names:
                tag = tman.add_tag(t)
                regex.tags.append(tag)
        self.session.commit()
        
    def remove_regex(self, regex):
        """Remove a regex definition"""

    def auto_tag(self, month):
        """Auto tag all transactions in a month against all defined regex"""
        regexs = self.regex_list(with_tags=False).to_dict(orient='records')
        regex = {}
        for r in regexs:
            regex[r['regex_name']] = re.compile(r['regex_name'])

        tag_map = self.regex_list(tags_compressed=False).to_dict(orient='records')
        tm = TransactionManager()
        transactions = tm.untagged(month)

        for i, t in transactions.iterrows():
            for tmap in tag_map:
                if regex[tmap['regex_name']].search(t.description):
                    self.tagTransaction([t.id], [tmap['tag_name']])
