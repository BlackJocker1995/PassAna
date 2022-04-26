/**
 * @name find string
 * @kind problem
 * @problem.severity warning
 * @id java/example/empty-block
 */

import java

from Argument arg, string text, string name, string location, string line
where
arg.getType() instanceof  TypeString and
text = arg.toString() and
text.length() >= 6 and
name = text and
line = arg.getLocation().getStartLine().toString() and
location = arg.getLocation().toString()

select name, text, line, location