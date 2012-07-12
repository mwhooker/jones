# TODO
   * Add versions to services controller. (DONE)
   * Implement update. (DONE)
   * fuck modals. just drop a textinput below the li/tr (DONE)
   * Mechanism for creating new services. (DONE)
   * UI. Adding a child should redirect you to that node (DONE)
   * Deleting root node should bounce you to index (DONE)
   * implement UI code for associations. (DONE)
   * UI. Deleting root node should prompt for confirmation
   * UI. Catch exceptions and flash messages (or do '/' validation)
   * validate node name client-side before accepting creation.
   * Support versions, rollback, and pegging to a version
       * Log every action so we can recreate in case of accident.
   * show raw json view.
   * add tooltips to inherited view and associations.
   * warn user if their update failed because of version conflict
      * preserve user's changes
   * use backbone.js for associations.
   * monitor zk connection state
      * if no connection can be made, send app into reduced functionality mode
   * integration tests

# Kazoo
implement:
  walk (DONE)
  resolve (DONE)
  ln (DONE)
test:
  ZNodeLink (DONEish)
fix:
 travis-ci
