import os

class DefaultConfig:
    def __init__(self):
        self._config = """
  [firstbit]
  <!doctype html>
  <html lang="en">
  <head>
  <meta charset="utf-8">
  <meta name="generator" content="jemdoc, see http://jemdoc.jaboc.net/" />
  <meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <script type="text/x-mathjax-config">
  MathJax.Hub.Config({
    tex2jax: {
      inlineMath: [['$','$'], ['\\(','$\\)']],
      displayMath: [['$$','$$'], ['$\\[','$\\]']]
    },
    TeX: { 
      extensions: ["AMScd.js", "action.js", "autobold.js", "cancel.js", "begingroup.js", "color.js", "enclose.js"] 
    }
  });
  </script>
  <script type="text/javascript" async src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-MML-AM_CHTML"></script>
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
  
  [defaultcss]
  <link rel="stylesheet" href="jemdoc.css" type="text/css" />
  
  [windowtitle]
  <title>|</title>

  [fwtitlestart]
  <div class="jumbotron text-center" id="fwtitle">

  [fwtitleend]
  </div>

  [navstart]
  <nav class="navbar navbar-expand-lg navbar-light bg-light %s" id="%s">
  <!-- <a class="navbar-brand" href="#">Navbar</a> = Navbar Brand -->
  <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNavAltMarkup" aria-controls="navbarNavAltMarkup" aria-expanded="false" aria-label="Toggle navigation">
  <span class="navbar-toggler-icon"></span>
  </button>
  <div class="collapse navbar-collapse" id="navbarNavAltMarkup">
  <div class="navbar-nav nav-fill w-100">

  [navend]
  </div>
  </div>
  </nav>

  [currentnavitem]
  <a class="nav-item nav-link active" href="|1">|2</a>

  [navitem]
  <a class="nav-item nav-link" href="|1">|2</a>

  [nonav]
  <div class="title-divider"></div>

  [doctitle]
  <div class="toptitle">
  <h1>|</h1>
  
  [subtitle]
  <h2 id="subtitle">|</h2>
  
  [doctitleend]
  </div>
  
  [bodystart]
  </head>
  <body>
  
  [analytics]
  <script type="text/javascript">
  var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
  document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
  </script>
  <script type="text/javascript">
  try {
      var pageTracker = _gat._getTracker("|");
      pageTracker._trackPageview();
  } catch(err) {}</script>
  
  [menustart]
  <main class="container" id="tlayout">
  <div class="row">
  <!-- Side menu -->
  <aside class="col-12 col-md-3 %s" id="%s"> 
  <ul class="nav nav-pills flex-column">
  
  [menuend]
  </ul>
  </aside>
  <div class="col-12 col-md-9" id="main-content">
  
  [menucategory]
  <div class="menu-category">|</div>

  [menuitem]
  <li class="nav-item menu-item"><a href="|1" class="nav-link">|2</a></li>

  [specificcss]
  <link rel="stylesheet" href="|" type="text/css" />

  [specificjs]
  <script src="|.js" type="text/javascript"></script>
  
  [currentmenuitem]
  <li class="nav-item menu-item"><a href="|1" class="nav-link active">|2</a></li>
  
  [nomenu]
  <div id="main-content">
  
  [menulastbit]
  <!-- End of main body -->
  </div>
  </div>
  </main>
  
  [nomenulastbit]
  </div>
  
  [bodyend]
  <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
  </body>
  </html>
  
  [infoblock]
  <div class="infoblock">
  
  [codeblock]
  <div class="codeblock">
  
  [blocktitle]
  <div class="blocktitle">|</div>
  
  [infoblockcontent]
  <div class="blockcontent">
  
  [codeblockcontent]
  <div class="blockcontent"><pre>
  
  [codeblockend]
  </pre></div></div>
  
  [codeblockcontenttt]
  <div class="blockcontent"><tt class="tthl">
  
  [codeblockendtt]
  </tt></div></div>
  
  [infoblockend]
  </div></div>
  
  [footerstart]
  <footer class="jumbotron" id="footer">
  <div id="footer footer-text">
  
  [footerend]
  </div>
  </footer>
  
  [lastupdated]
  Page generated |, by <a href="http://jemdoc.jaboc.net/">jemdoc</a>.

  [sourcelink]
  (<a href="|">source</a>)

  """

    def downloadStandardConfig(self):
        filename = "standardconfig.txt"
        filePath = os.path.join(".", filename)
        fileObj = open(filePath, "w")
        print "Downloading standard configuration file %s..." % filename
        fileObj.write(self._config)
        fileObj.flush()
        fileObj.close()

    def getStandardConfig(self):
        return self._config