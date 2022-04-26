/**
 * @name find string
 * @kind problem
 * @problem.severity warning
 * @id cpp/example/empty-block
 */

import cpp


from Variable var, string text
where var.getInitializer().getExpr().getActualType().toString() = "const char *" and
text = var.getInitializer().getExpr().getValue() and
(text != "0" and text != "[empty string]" and text.length() >= 6)
select var.getName().toString(), var.getInitializer().getExpr().getValue(), var.getInitializer().getLocation().getStartLine(), var.getInitializer().getLocation()

