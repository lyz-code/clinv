# Todo

## HH

### H

* Add `clinv verify` to test:
  * No user has changed it's policies attached
  * No group has changed it's policies attached
  * The group members are the ones that we desired
  * Check if 2fa is enabled for users with password
  * the access keys are updated

* Add IAM policy, roles and instance profiles support
* Add comments to ec2 instances, projects, services and informations

### M

* Add risk management support
* Autoscaling group support
* Add to `clinv verify` to check if there are deleted or terminated aws resources assigned to
  projects.
* Create an input method `clinv create service`
* Create an edit method `clinv edit ser_01`
* Refactor the Source tests into a parent testcase to avoid duplicated code
* Service object access part divided by user type with each it's type of access
and information it access
* Add related subcommand to get what resources are associated with a defined
  resource (with the optional -n flag to specify the levels of association)
* Improve service search so if the children resources match, the service
matches.
* Search also into the terminated resources with a specific flag. But by
  default don't search on terminated (add a if self.state == terminated return
  False on ClinvGenericResource.search()). (refactor from list services)
* Read the description from the AWS resources

### L

* Automatic alphabetic reindex of informations, services and projects when c generate
* Terminated report that shows the resources of terminated services, to check
if they should be destroyed
* Create the --json flag for reports
