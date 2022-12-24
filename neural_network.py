import onnxruntime
import numpy as np

class onnx_model_wrapper():
    def __init__(self, onnx_model_path="./policy_value_network.onnx"):
        self.policy_value_net_sesion = onnxruntime.InferenceSession(onnx_model_path)
    
    def policy_value_fn(self, board):
        legal_positions = board.availables
        current_state = self.transNetInput(board.current_state())
        log_act_probs, value = self.policy_value_net_sesion.run(None, {"input": current_state})
        act_probs = np.exp(log_act_probs.flatten())
        act_probs = zip(legal_positions, act_probs[legal_positions])
        value = value[0]
        return act_probs, value


    def transNetInput(self, origin_input):
        trans_input = origin_input[:3]
        for i in range(0, 3):
            trans_input[i] = np.flip(trans_input[i], 0)
        trans_input = np.ascontiguousarray([trans_input])
        trans_input = trans_input.astype(np.float32)
        return trans_input

