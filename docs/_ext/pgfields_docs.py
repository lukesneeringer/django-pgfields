from sphinx import addnodes
from sphinx.util.compat import Directive


def setup(app):
    app.add_directive('version_added', VersionDirective)
    app.add_directive('version_changed', VersionDirective)
    app.add_config_value('next_version', '1.0', True)


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

        # Create and append the node.
        node = addnodes.versionmodified(
            text='New in %s.' % version_string,
        )
        answer.append(node)

        # Place the node into the contents.
        node['type'] = self.name
        node['version'] = version
        node['style'] = 'font-size: 60%; text-style: italic;'

        # Done. Return the answer.
        return answer
