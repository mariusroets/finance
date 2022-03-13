from .models import Regex
from .dbmanager import DBManager
from .tags import Tags

class AutoTags(DBManager):
    """Class that handles auto tagging, maintaining the settings for
    auto tagging"""

    def regex_exists(self, regex_name):
        """Test if a given regex exists in the database

        :regex_name (str): TODO
        :returns (bool): TODO

        """
        regex = self.session.query(Regex).filter_by(name = regex_name).one_or_none()
        return regex if regex else False

    def add_regex(self, regex_name):
        """Adds a new regex to the databse

        :regex_name: TODO
        :returns: TODO

        """
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
        tags = Tags(self.session)
        for r in regex_names:
            regex = self.add_regex(r)
            for t in tag_names:
                tag = tags.add_tag(t)
                regex.tags.append(tag)
        self.session.commit()

