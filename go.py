#!/usr/bin/env python

"""
Game of GO.
"""

import copy
import numpy as np
import scipy.ndimage
import matplotlib.widgets
import pylab

pylab.ion()

############################################################

class go:

    def __init__(self, n, handicap=0):

        self.welcome()

        self.n = n
        self.handicap = handicap
        self.board = [np.zeros((self.n, self.n))]

        self.f, self.ax = pylab.subplots(figsize=(8, 9))
        self.ax._label = 'main'
        pylab.subplots_adjust(bottom=0.2)
        self.f.set_facecolor('tan')
        pylab.axes(axisbg='tan')

        #pylab.grid(ls='-', zorder=0)
        pylab.vlines(np.arange(self.n - 1), 0, self.n - 1, zorder=-1)
        pylab.hlines(np.arange(self.n - 1), 0, self.n - 1, zorder=-1)
        pylab.xticks(np.arange(self.n))
        pylab.yticks(np.arange(self.n))
        pylab.xlim(-0.5, self.n - 0.5)
        pylab.ylim(-0.5, self.n - 0.5)

        self.turn = 0
        self.marker = 1 # 1 = black, -1 = white
        self.score = [[0, 0]] # Captured stones (negative is bad)
        self.territory = [0, 0] # Enclosed territory (positive is good)

    def plot(self, clear=False):
        if (np.sum(self.turn) > 1) or clear:
            pylab.cla()
        pylab.axes(axisbg='tan', frameon=False)
        self.getTerritory()
        if self.handicap:
            if self.turn <= self.handicap:
                self.marker = 1

        pylab.title('Turn %i: %s\'s move\nWhite: %i (+%i)%sBlack: %i (+%i)'%(self.turn, 
                                                                             'Black' if self.marker == 1 else 'White',
                                                                             self.score[self.turn][0],
                                                                             self.territory[0],
                                                                             ' ' * 45,
                                                                             self.score[self.turn][1],
                                                                             self.territory[1]))
        #pylab.grid(ls='-', zorder=0)
        pylab.vlines(np.arange(self.n), 0, self.n - 1, zorder=-1)
        pylab.hlines(np.arange(self.n), 0, self.n - 1, zorder=-1)
        #pylab.xticks(np.arange(self.n))
        pylab.xticks([])
        #pylab.yticks(np.arange(self.n))
        pylab.yticks([])
        pylab.xlim(-0.5, self.n - 0.5)
        pylab.ylim(-0.5, self.n - 0.5)

        xx, yy = np.meshgrid(np.arange(self.n), np.arange(self.n)) 
        cut = (self.board[self.turn].flatten() != 0)
        if np.sum(cut) > 0:
            #pylab.scatter(xx.flatten()[cut], yy.flatten()[cut], c=self.board[self.turn].flatten()[cut], 
            #              s=500, cmap='binary', vmin=-1, vmax=1, zorder=-1)
            pylab.scatter(xx.flatten()[cut], yy.flatten()[cut], c=self.board[self.turn].flatten()[cut], 
                          s=(5500. / self.n), cmap='binary', vmin=-1, vmax=1, zorder=-1)

    def onclick(self, event):
        if event.inaxes._label in ['pass', 'previous', 'next']:
            pass
        elif self.board[self.turn][np.round(event.ydata), np.round(event.xdata)] != 0:
            print '  ...that space is already taken...'
        else:
            if self.turn < (len(self.board) - 1):
                # Need to clear the board and score
                n_clear = (len(self.board) - 1) - self.turn
                for ii in range(0, n_clear):
                    self.board.pop(-1)
                    self.score.pop(-1)
            self.board.append(copy.deepcopy(self.board[self.turn]))
            self.score.append(copy.deepcopy(self.score[self.turn]))
            self.turn += 1
            self.board[self.turn][np.round(event.ydata), np.round(event.xdata)] = self.marker
            self.marker *= -1

            self.capture()
            self.plot()

    def passTurn(self, event):
        self.marker *= -1
        self.plot(clear=True)

    def prev(self, event):
        if self.turn == 0:
            print '  ...already on first move...'
        else:
            self.turn -= 1
            self.marker *= -1
            print '  ...back to turn %i...'%(self.turn)
            self.plot(clear=True)

    def next(self, event):
        if self.turn == (len(self.board) - 1):
            print '  ...already on most recent move...'
        else:
            self.turn += 1
            self.marker *= -1
            print '  ...ahead to turn %i...'%(self.turn)
            self.plot(clear=True)

    def capture(self):
        self.captureMarker(self.marker)
        self.captureMarker(self.marker * -1)

    def captureMarker(self, marker):
        board_label, n_cluster = scipy.ndimage.label(self.board[self.turn] == marker)
        for index_cluster in range(1, n_cluster + 1):
            board_free = scipy.ndimage.binary_dilation(board_label == index_cluster).astype(int)
            board_survive = board_free & (board_label != index_cluster) & (self.board[self.turn] == 0)
            if not np.any(board_survive):
                n_capture = np.sum(board_label == index_cluster)
                print '  ...%s captures %i stone%s...'%('white' if marker == 1 else 'black', 
                                                        n_capture,
                                                        '' if n_capture == 1 else 's' )
                self.board[self.turn][board_label == index_cluster] = 0
                self.score[self.turn][int(marker > 0)] -= n_capture

    def getTerritory(self):
        self.territory = [0, 0]
        if self.turn > 0:
            board_label, n_territory = scipy.ndimage.label(self.board[self.turn] == 0)
            for index_territory in range(1, n_territory + 1):
                board_perimeter = scipy.ndimage.binary_dilation(board_label == index_territory).astype(int)
                board_perimeter = board_perimeter & ~(board_label == index_territory)
                for ii, marker in enumerate([-1, 1]):
                    if np.all(self.board[self.turn][board_perimeter.astype(bool)].astype(int) == marker):
                        self.territory[ii] += np.sum(board_label == index_territory)

    def welcome(self):
        welcome_message = """
        LET'S PLAY...
         _____  ______
        /      /     /
       /  __  /  /  /
      /____/ /_____/
        """
        
        print welcome_message

############################################################

if __name__ == "__main__":
    
    import argparse
    description = __doc__
    formatter = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=formatter)
    parser.add_argument('-n', '--size', default=11, type=int,
                        help='Size of board (n x n) ')
    parser.add_argument('-H', '--handicap', default=0, type=int,
                        help='Number of handicap stones')
    args = parser.parse_args()

    game = go(args.size, handicap=args.handicap)
    game.plot()
    
    cid = game.f.canvas.mpl_connect('button_press_event', game.onclick)

    axpass = pylab.axes([0.59, 0.05, 0.1, 0.075])
    axpass.set_label('pass')
    axprev = pylab.axes([0.7, 0.05, 0.1, 0.075])
    axprev.set_label('previous')
    axnext = pylab.axes([0.81, 0.05, 0.1, 0.075])
    axnext.set_label('next')
    bpass = matplotlib.widgets.Button(axpass, 'Pass', color='tan', hovercolor='silver') # peru, silver, lime
    bpass.on_clicked(game.passTurn)
    bnext = matplotlib.widgets.Button(axnext, 'Next', color='tan', hovercolor='silver')
    bnext.on_clicked(game.next)
    bprev = matplotlib.widgets.Button(axprev, 'Previous', color='tan', hovercolor='silver')
    bprev.on_clicked(game.prev)
    

    raw_input('PRESS "RETURN" TO END GAME')

############################################################
