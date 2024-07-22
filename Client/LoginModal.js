import React from "react";
import { Button, Modal } from "react-bootstrap";

function LoginModal({ close_modal }) {
  return (
    <Modal.Dialog>
      <Modal.Header>
        <Modal.Title>Error</Modal.Title>
      </Modal.Header>

      <Modal.Body>
        <p>please enter valid username and password</p>
      </Modal.Body>

      <Modal.Footer>
        <Button
          variant="secondary"
          onClick={() => {
            close_modal(false);
          }}
        >
          Close
        </Button>
      </Modal.Footer>
    </Modal.Dialog>
  );
}

export default LoginModal;
