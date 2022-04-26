/**
 * @name find string
 * @kind problem
 * @problem.severity warning
 * @id csharp/example/empty-block
 */

import csharp


from Variable var, string text, string name, string namestr
where
var.getType() instanceof  StringType and
text = var.getInitializer().toString() and
name = var.getName().toString() and
namestr = text.toLowerCase() and
text.length() >=6 and
(namestr.regexpMatch("\\w*password\\w*") or
namestr.regexpMatch("\\w*passwd\\w*") or
namestr.regexpMatch("\\w*pwd\\w*") or
namestr.regexpMatch("\\w*secret\\w*") or
namestr.regexpMatch("\\w*token\\w*") or
namestr.regexpMatch("\\w*auth\\w*") or
      namestr.regexpMatch("\\w*security\\w*") or
      namestr.regexpMatch("\\w*seed\\w*")
)
select var.getName().toString(),
text,
var.getInitializer().getLocation().getStartLine().toString(),
var.getInitializer().getLocation().toString()