from .dbmanager import Connection
from .models import Tag

class Tags(Connection):
    """Manages tags and everything associated with maintaining tags"""

    def tags(self):
        """Returns a list of all tags"""
        return self.query(
            self.session
            .query(Tag)
            .order_by(Tag.name)
        )

    def tag_exists(self, tag_name):
        """Checks whether a tag exists in the database

        :tag_name: TODO
        :returns: TODO

        """
        tag = self.session.query(Tag).filter_by(name=tag_name).one_or_none()
        return tag if tag else False

    def add_tag(self, tag_name, description=""):
        """Adds a new tag to the database

        :tag_name: TODO
        :returns: TODO

        """
        tag = self.tag_exists(tag_name)
        if tag:
            return tag
        tag = Tag(name=tag_name, description=description)
        self.session.add(tag)
        self.session.commit()
        return tag

    def remove_tag(self, tag_name):
        """Removes the given tag from the database. Tags will be remove from all transactions,
        autotags and groups.

        Args:
            tag_name (TODO): TODO

        Returns: TODO

        """
        pass

    def clear_tags(self):
        """Remove all tags that are not used anywhere in the database

        Returns: TODO

        """
        pass
