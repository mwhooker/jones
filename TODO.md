# TODO
   * Add versions to services controller. (DONE)
   * Implement update. (DONE)
   * fuck modals. just drop a textinput below the li/tr (DONE)
   * Mechanism for creating new services. (DONE)
   * UI. Adding a child should redirect you to that node
   * UI. Deleting root node should bounce you to index
   * Support versions, rollback, and pegging to a version
       * Log every action so we can recreate in case of accident.
   * Prompt user for confirmation before deleting node.
   * validate node name client-side before accepting creation.
   * show raw json view.
   * implement UI code for associations. (DONE)
   * add tooltips to inherited view and associations.
   * warn user if their update failed because of version conflict
      * preserve user's changes
   * use backbone.js so we don't lose settings during page reload
   * Move jones.py into an outside lib
