/**
 * @name find string
 * @kind problem
 * @problem.severity warning
 * @id python/example/empty-scope
 */

import python

from Argument stmt, Unicode s, Name n
where stmt.getValue() instanceof Unicode and
stmt.getATarget() instanceof Name and
s = stmt.getValue() and
n = stmt.getATarget() and
s.getText().length() > 5 and
s.getText().length() <= 256 and
s.getLocation().toString().regexpMatch("/opt/src.*") and
n.getId().toString().substring(0, 2) != "__"
select n.getId(), s.getText(), n.getLocation().getStartLine(), n.getLocation()
