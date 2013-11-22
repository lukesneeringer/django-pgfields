import os
from sphinx import addnodes
from sphinx.util.compat import Directive


def setup(app):
    app.add_directive('versionadded', VersionDirective)
    app.add_directive('versionchanged', VersionDirective)
    app.add_config_value('next_version', '1.4', True)


class VersionDirective(Directive):
    """Directive class for adding version notes."""

    has_content = True
    required_arguments = 1
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {}

    def run(self):
        """Translate the directive to the appropriate markup."""
        answer = []

        # Sanity Check: This directive only understands one argument.
        if len(self.arguments) != 1:
            raise self.error('%s takes exactly one argument.' % self.name)

        # Get the environment, which knows things like what
        # the next version will be.
        env = self.state.document.settings.env

        # Determine what the version is
        if self.arguments[0] == env.config.next_version:
            version = 'Development'
            version_string = 'development version'
        else:
            version = self.arguments[0]
            version_string = 'version %s' % version

        # Determine the proper node text.
        # This should be simple, but Read the Docs misbehaves
        #   (and does so in a totally undocumented way). Sigh.
        kwargs = {}
        if not os.environ.get('READTHEDOCS', None):
            kwargs['text'] = 'New in %s.' % version_string

        # Create and append the node.
        node = addnodes.versionmodified(**kwargs)
        answer.append(node)

        # Place the node into the contents.
        node['type'] = self.name
        node['version'] = version
        node['style'] = 'font-size: 60%; text-style: italic;'

        # Done. Return the answer.
        return answer
