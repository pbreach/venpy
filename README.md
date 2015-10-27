# VenPy
Python Tools for Vensim

 

This package provides a pure Python wrapper to the [Vensim system dynamics simulation software](http://vensim.com) through the Vensim DLL. The Vensim DLL provides the ability to develop interfaces for pre-existing models by allowing access to some of the tools and functions used in the software itself. 

##Goals

1. Provide easy access to existing Vensim functionality in Python. This will help to facilitate:
  * Batch processing of simulation runs under a range of exogenously driven scenarios or events.
  * Incorporation of changes in model structure over time.
  * Communication between separate models.

2. Allow for the inclusion of non-existant Vensim features such as:
  * Spatially distributed models through communication with other software(s) such as ArcGIS.
  * The use of existing and new software being developed in the scientific Python community.

##Focus

The goals of this project are very much in line with [PySD](https://github.com/JamesPHoughton/pysd) and is in no way a     replacement for this effort. In this project there is a specific focus on *Vensim* models through the DLL. This includes the use of *all* Vensim functions (depending on whether the DSS or PLE versions are installed) and features which are not available in other system dynamics simulation programs ([Stella](http://www.iseesystems.com/softwares/Education/StellaSoftware.aspx), [Simulink](https://en.wikipedia.org/wiki/Simulink), [MapleSim](https://en.wikipedia.org/wiki/MapleSim), etc.).

##Limitations

* The use of the Vensim DLL through this package can only support Windows (as far as I know)
* The version of Python must match the bitness of the Vensim version (which mainly provides 32-bit)
* Larger models will have the same performance limitations as the Vensim software
* Only constants and 'Gaming' type auxiliary variables can be set before and during simulations respectively
* Those who have Vensim PLE installed will only be able to modify model constants prior to simulation
* Potential compatibility issues with future versions of Vensim
* Likely more to come...

##Applications

Although these limitations do exist, the Vensim DLL has been used in many successful applications to extend Vensim Functionality. Some of these include the works of:

   [Peck, A., Neuwirth, C., Simonovic, S.P. (2014). "Coupling System Dynamics with Geographic Information Systems". Water Resources Research Report no.086, Facility for Intelligent Decision Support, Department of Civil and Environmental Engineering, London, Ontario, Canada, 81 pages. ISBN (print) 978-0-7714-3067-1; (online) 978-0-7714-3068-8.](http://www.eng.uwo.ca/research/iclr/fids/publications/products/86.pdf)

   [Srivastav, R., and Simonovic, S.P. (2014). "Generic Framework for Computation of Spatial 
Dynamic Resilience". Water Resources Research Report no. 085, Facility for Intelligent Decision Support, 
Department of Civil and Environmental Engineering, London, Ontario, Canada, 81 pages. ISBN: (print) 
978-0-7714-3067-1; (online) 978-0-7714-3068-8.](http://www.eng.uwo.ca/research/iclr/fids/publications/products/85.pdf)




