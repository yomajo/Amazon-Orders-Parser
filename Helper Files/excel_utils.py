

def get_last_used_row_col(ws:object):
    '''returns dictionary containing max_row and max_col as integers - last used row and column in passed openpyxl worksheet'''
    row = ws.max_row
    while row > 0:
        cells = ws[row]
        if all([cell.value is None for cell in cells]):
            row -= 1
        else:
            break
    if row == 0:
        return {'max_row' : 0, 'max_col' : 0}

    column = ws.max_column
    while column > 0:
        cells = next(ws.iter_cols(min_col=column, max_col=column, max_row=row))
        if all([cell.value is None for cell in cells]):
            column -= 1
        else:
            break
    return {'max_row' : row, 'max_col' : column}

def cell_to_float(cell_value:str):
    '''returns float for ws data dict whenever possible'''
    try:
        return float(cell_value)
    except ValueError:
        return cell_value
    except TypeError:
        return None


if __name__ == '__main__':
    pass