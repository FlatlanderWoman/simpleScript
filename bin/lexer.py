# coding=utf-8
"""Represents a Tokenizer of Tokens."""

from bin.constants import *
from bin.errors import IllegalCharError, ExpectedCharError
from bin.position import Position
from bin.token import Token


class Lexer:
    """The lexical analyzer component of the language."""

    def __init__(self, input_text, fn):
        """
        Create instance of a Lexer.
        :param input_text: Input stream to parse using Lexer.
        :param fn: File name of the document.
        """
        self.text = input_text
        self.position = Position(-1, 0, -1, fn, input_text)
        self.current_character = None
        self.advance()  # 0-indexed array repr
        self.fn = fn

    def advance(self):
        """Advance the position of the input stream."""
        self.position.advance(self.current_character)
        self.current_character \
            = self.text[self.position.idx] if self.position.idx < len(self.text) else None

    def tokenize(self):
        """
        Tokenize the input text stream.
        :return: List of Token instances and/or Error instances.
        """
        tokens = []
        while self.current_character is not None:

            chars_to_skip = [' ', '\t']
            if self.current_character in chars_to_skip:
                self.advance()  # Skip useless chars

            # Transform input stream into a number Token
            elif self.current_character in DIGITS:
                tokens.append(self.make_number())

            # Transform input stream into an identifier Token
            elif self.current_character in LETTERS:
                tokens.append(self.make_identifier())

            # All maths and grouping operators
            elif self.current_character == '+':
                tokens.append(Token(TP_PLUS, start_pos=self.position))
                self.advance()
            elif self.current_character == '-':
                tokens.append(Token(TP_MINUS, start_pos=self.position))
                self.advance()
            elif self.current_character == '*':
                tokens.append(Token(TP_MUL, start_pos=self.position))
                self.advance()
            elif self.current_character == '^':
                tokens.append(Token(TP_POWER, start_pos=self.position))
                self.advance()
            elif self.current_character == '/':
                tokens.append(Token(TP_DIV, start_pos=self.position))
                self.advance()
            elif self.current_character == '|':
                tokens.append(Token(TP_CLEAN_DIV, start_pos=self.position))
                self.advance()
            elif self.current_character == '%':
                tokens.append(Token(TP_MODULO, start_pos=self.position))
                self.advance()
            elif self.current_character == '(':
                tokens.append(Token(TP_LPAREN, start_pos=self.position))
                self.advance()
            elif self.current_character == ')':
                tokens.append(Token(TP_RPAREN, start_pos=self.position))
                self.advance()

            # Comparison and boolean operators
            elif self.current_character == '!':
                token, error = self.make_not_equals()
                if error:
                    return [], error
                tokens.append(token)
            elif self.current_character == '=':
                tokens.append(self.make_equals())
            elif self.current_character == '<':
                tokens.append(self.make_less_than())
            elif self.current_character == '>':
                tokens.append(self.make_greater_than())

            # Tokenize all remaining possible characters
            else:  # Report all illegal chars in stream
                start_pos = self.position.copy()
                illegal_character = self.current_character
                self.advance()  # Note: Advance to ensure pointer doesn't detach
                return [], IllegalCharError('"' + illegal_character + '"', start_pos, self.position)

        # Mark end with EOF and return
        tokens.append(Token(TP_EOF))
        return tokens, None

    def make_number(self):
        """
        Turn text stream into either a float or an int Token.
        :return: Either a TP_FLOAT or a TP_INT number Token instance.
        """
        number_str, dot_count = '', 0
        start_pos = self.position.copy()
        while self.current_character is not None \
                and self.current_character in DIGITS + '.':
            if self.current_character == '.':
                if dot_count == 1:
                    break  # Max one dot per float
                dot_count += 1
            number_str += self.current_character
            self.advance()

        # Tokenize the numeric value to INT or FLOAT types
        if dot_count == 0:  # Tokenize an INT data type
            return Token(TP_INT, int(number_str), start_pos, self.position)
        else:  # Must be FLOAT data type
            return Token(TP_FLOAT, float(number_str), start_pos, self.position)

    def make_identifier(self):
        identifier_str = ''
        start_pos = self.position.copy()
        while self.current_character is not None and self.current_character in LETTERS + DIGITS + '_':
            identifier_str += self.current_character
            self.advance()
        token_type = TP_KEYWORD if identifier_str in KEYWORDS else TP_IDENTIFIER
        return Token(token_type, identifier_str, start_pos, self.position)

    def make_not_equals(self):
        """
        Makes a not-equals Token if the '!=' chars are found.
        :return: Token for the not-equals symbol in the lexer.
        """
        start_pos = self.position.copy()
        self.advance()
        if self.current_character == '=':
            self.advance()
            return Token(TP_NE, start_pos=start_pos, end_pos=self.position), None
        self.advance()
        return None, ExpectedCharError('Expected an "=" character after a "!" character.',
                                       start_pos,
                                       self.position)

    def make_dual_use_token(self, initial_type, alternate_type, ):
        """
        Returns one of two Token types given the character string.
        :param initial_type: Initial possible type of the Token.
        :param alternate_type: Alternate Token type given the successive character.
        :return: Token with either of the two possible types.
        """
        token_type = initial_type
        start_pos = self.position.copy()
        self.advance()
        if self.current_character == '=':
            self.advance()
            token_type = alternate_type
        return Token(token_type, start_pos, self.position)

    def make_equals(self):
        """
        Creates either a single equals or a double equals Token.
        :return: Token with either a single or a double equals type.
        """
        return self.make_dual_use_token(TP_EQUALS, TP_EE)

    def make_less_than(self):
        """
        Creates either a less or a less-than Token.
        :return: Token with either a less or a less-than type.
        """
        return self.make_dual_use_token(TP_LT, TP_LTE)

    def make_greater_than(self):
        """
        Creates either a greater or a greater-than Token.
        :return: Token with either a greater or a greater-than type.
        """
        return self.make_dual_use_token(TP_GT, TP_GTE)
