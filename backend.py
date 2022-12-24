import http.server
import json
from MCTS import MCTSPlayer
from game_map import SessionMap
from game import Board, Game
from neural_network import onnx_model_wrapper

gameDict = SessionMap(20, 10)
policy_value_net_onnx_wrapper = onnx_model_wrapper()
mcts_player = MCTSPlayer(policy_value_net_onnx_wrapper.policy_value_fn, c_puct=5, n_playout=2)

class RequestHandlerImpl(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("别curl我了，我这里啥也没实现\n".encode("utf-8"))

    def do_POST(self):
        if self.path == '/gomoku/api/start':
            req_body = self.rfile.read(int(self.headers["Content-Length"])).decode()
            parsed_json = json.loads(req_body)
            sessionID = parsed_json["session_id"]
            startController(sessionID, gameDict)
            self.resSuccess('{"message":"success"}')
        elif self.path == '/gomoku/api/restart': 
            req_body = self.rfile.read(int(self.headers["Content-Length"])).decode()
            parsed_json = json.loads(req_body)
            oldSessionID, newSessionID = parsed_json["old_session_id"], parsed_json["new_session_id"]
            restartController(oldSessionID, newSessionID, gameDict)
            self.resSuccess('{"message":"success"}')
        elif self.path == '/gomoku/api/move':
            req_body = self.rfile.read(int(self.headers["Content-Length"])).decode()
            parsed_json = json.loads(req_body)
            x, y, sessionID = parsed_json["coor_x"], parsed_json["coor_y"], parsed_json["session_id"]
            try:
                ai_x, ai_y, end, winner = moveController(sessionID, gameDict,x, y, mcts_player)
            except:
                ai_x, ai_y, end, winner = 0, 0, 0, -100
                gameDict.GameMap.clear()

            respDict = {"x":int(ai_x), "y":int(ai_y), "end": end, "winner": winner}
            jstr = json.dumps(respDict)
            self.resSuccess(json.dumps(respDict))

    def resSuccess(self, message):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write((message).encode("utf-8"))


def startController(sessionID, gameDict):
    if not gameDict.getGameBySessionID(sessionID):
        # new board
        board = Board(width=15, height=15, n_in_row=5)
        game = Game(board)
        gameDict.createGame(game, sessionID)
        game.board.init_board(0)
        
def restartController(oldSessionID, newSessionID, gameDict):
    # new Board
    gameDict.delGame(oldSessionID)
    board = Board(width=15, height=15, n_in_row=5)
    game = Game(board)
    gameDict.createGame(game, newSessionID)
    game.board.init_board(0)

def moveController(sessionID, gameDict, x, y, mctsp):
    item = gameDict.getGameBySessionID(sessionID)
    if not item:
        raise [ValueError["get game by sessionID failed"]]
    game = item[0]
    game.board.do_move(getIndex(x, y))
    end, winner = game.board.game_end()
    if end:
        gameDict.delGame(sessionID)
        return 0, 0, True, 1
    action = mctsp.get_action(game.board)
    game.board.do_move(action)
    end, winner = game.board.game_end()
    ai_x, ai_y = getCoor(action)
    if end:
        gameDict.delGame(sessionID)
    return ai_x, ai_y, end, winner 

def getIndex(x, y):
    return 15*x + y

def getCoor(index):
    return index//15, index%15

if __name__ == "__main__":
    # new dict
    # new server
    server_address = ("", 9999)
    httpd = http.server.HTTPServer(server_address, RequestHandlerImpl)
    httpd.serve_forever()
