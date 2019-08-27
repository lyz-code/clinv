# Todo

## HH

### H

* Refactor clinv reports and inventory to their own objects
  * Once you do that, split the tests as TestRoute53Inventory
  * Give it a think how to use a Plugin model, thinking the contribution as
  plugins for the resources, and then reports.
* Add comments to ec2 instances, projects, services and informations

### M

* Add risk management support
* Autoscaling group support
* Service object access part divided by user type with each it's type of access
and information it access
* Add related subcommand to get what resources are associated with a defined
  resource (with the optional -n flag to specify the levels of association)
* Improve service search so if the children resources match, the service
matches.
* Search also into the terminated resources with a specific flag. But by
  default don't search on terminated (add a if self.state == terminated return
  False on ClinvGenericResource.search()). (refactor from list services)

### L

* Automatic alphabetic reindex of informations, services and projects when c generate
* Terminated report that shows the resources of terminated services, to check
if they should be destroyed
* Create the --json flag for reports


