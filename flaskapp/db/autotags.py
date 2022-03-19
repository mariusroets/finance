from .models import Regex
from .dbmanager import Connection
from .tags import Tags

class AutoTags(Connection):
    """Class that handles auto tagging, maintaining the settings for
    auto tagging"""

    def link_regex_tag(self, tag_names, regex_names):
        """Links the given tag to a regex

        :tag_name: TODO
        :regex_id: TODO
        :returns: TODO

        """
        tags = Tags(self.session)
        reg = RegexManager(self.session)
        for r in regex_names:
            regex = reg.add_regex(r)
            for t in tag_names:
                tag = tags.add_tag(t)
                regex.tags.append(tag)
        self.session.commit()

