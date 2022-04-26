/**
 * @name find string
 * @kind problem
 * @problem.severity warning
 * @id cpp/example/empty-block
 */

import cpp


from Variable var, string namestr, string text
where var.getInitializer().getExpr().getActualType().toString() = "const char *" and
text = var.getInitializer().getExpr().getValue() and
namestr = var.getName() and
(text != "0" and text != "[empty string]" and text.length() >= 6) and
	(namestr.regexpMatch("\\w*password\\w*") or
     namestr.regexpMatch("\\w*passwd\\w*") or
      namestr.regexpMatch("\\w*pwd\\w*") or
      namestr.regexpMatch("\\w*secret\\w*") or
      namestr.regexpMatch("\\w*token\\w*") or
      namestr.regexpMatch("\\w*auth\\w*") or
      namestr.regexpMatch("\\w*security\\w*") or
      namestr.regexpMatch("\\w*seed\\w*")
)

select var.getName().toString(), var.getInitializer().getExpr().getValue(),
var.getInitializer().getLocation().getStartLine(), var.getInitializer().getLocation()