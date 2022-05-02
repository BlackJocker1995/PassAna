/**
 * @name find string
 * @kind problem
 * @problem.severity warning
 * @id python/example/empty-scope
 */

import python

from AssignStmt stmt, Unicode s, Name n, string namestr
where stmt.getValue() instanceof Unicode and
stmt.getATarget() instanceof Name and
s = stmt.getValue() and
n = stmt.getATarget() and
namestr = n.getId().toString().toLowerCase() and
(
	namestr.regexpMatch("\\w*password\\w*") or
     namestr.regexpMatch("\\w*passwd\\w*") or
      namestr.regexpMatch("\\w*pwd\\w*") or
      namestr.regexpMatch("\\w*secret\\w*") or
      namestr.regexpMatch("\\w*token\\w*") or
      namestr.regexpMatch("\\w*auth\\w*") or
      namestr.regexpMatch("\\w*security\\w*") or
      namestr.regexpMatch("\\w*seed\\w*") or
      namestr.regexpMatch("\\w*key\\w*")
) and
s.getText().length() > 5 and
s.getText().length() <= 256 and
s.getLocation().toString().regexpMatch("/opt/src.*") and
n.getId().toString().substring(0, 2) != "__"
select n.getId(), s.getText(), n.getLocation().getStartLine(), n.getLocation()