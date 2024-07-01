import pandas as pd

def transpose_excel(input_file, output_file):
    # Read the Excel file
    df = pd.read_excel(input_file)
    
    # Transpose the DataFrame
    df_transposed = df.T
    #Get rid of index header
    df_transposed.columns = df_transposed.iloc[0]
    # Save the transposed DataFrame back to an Excel file
    df_transposed.to_excel(output_file, index=False)

# Example usage
input_file = 'Test.xlsx'  # Replace with the path to your input Excel file
output_file = 'test_output.xlsx'  # Replace with the desired path for the output Excel file
transpose_excel(input_file, output_file)


'''
def realign_data(self):
        unamtched_pairs_color = []
        unmatched = []
        unmatched1 = []
        color_no_match = []
        matched_pairs_color = []
        table2_rows_taken = set()

        def is_white(color):
            return (color.red() == 255 and color.green() == 255 and color.blue() == 255) or (color.red() == 0 and color.green() == 0 and color.blue() == 0)

        # Step 1: Find all matches and categorize unmatched items
        for i in range(self.table1.rowCount()):
            item1 = self.table1.item(i, 0)
            if item1:
                word1 = item1.text()
                bg_color1 = item1.background().color()
                matched = False
                for j in range(self.table2.rowCount()):
                    if j in table2_rows_taken:
                        continue
                    item2 = self.table2.item(j, 0)
                    if item2:
                        word2 = item2.text()
                        bg_color2 = item2.background().color()
                        if (bg_color2 == bg_color1 and not is_white(bg_color2) and not is_white(bg_color1)):
                            matched_pairs_color.append((word1, word2))
                            if any(word1 in pair for pair in self.pairs_matched.keys()):
                                try:
                                    if not self.pairs_matched.get((word1, self.old_background[word1])):
                                        self.pairs_matched.pop((word1, self.old_background[word1]), None)
                                        self.color_match.pop((word1, self.old_background[word1]), None)
                                        # color_no_match.append((word1, self.old_background[word1]))
                                        table2_rows_taken.add(j)
                                        break
                                except:
                                    pass
                            self.pairs_matched[(word1, word2)] = True
                            self.color_match[(word1, word2)] = bg_color1
                            table2_rows_taken.add(j)
                            matched = True
                            break
                        elif is_white(bg_color2) and is_white(bg_color1):
                            unamtched_pairs_color.append((word1, word2))
                            table2_rows_taken.add(j)
                            matched = True
                            break

                if not matched:
                    if is_white(bg_color1):
                        unmatched1.append((word1, None))
                    elif not is_white(bg_color1) and any(True for pair in self.pairs_matched if self.pairs_matched[pair] and word1 in pair):
                        continue
                    else:
                        color_no_match.append((word1, None))

        # Step 2: Add remaining unmatched items from table2
        for i in range(self.table2.rowCount()):
            if i not in table2_rows_taken:
                item2 = self.table2.item(i, 0)
                if item2:
                    word2 = item2.text()
                    unmatched.append((None, word2))

        # Step 3: Clear and set up the tables
        self.table1.clear()
        count_dups = set()
        count = 0
        for pair in self.pairs_matched:
            if pair[1] not in count_dups:
                count_dups.add(pair[1])
            else:
                count += 1
        total_pairs = len(self.pairs_matched)
        total_pairs_b = len(self.pairs_matched) - count
        self.table1.setRowCount(total_pairs + len(unamtched_pairs_color) + len(unmatched1))
        self.table1.setColumnCount(1)
        self.table1.setHorizontalHeaderLabels(["Matched Headers"])
        self.table2.clear()
        self.table2.setRowCount(total_pairs_b + len(unamtched_pairs_color) + len(unmatched))
        self.table2.setColumnCount(1)
        self.table2.setHorizontalHeaderLabels(["Meta Data Matched Headers"])

        # Step 4: Fill in the tables with matched and unmatched items
        for i, (word1, word2) in enumerate(self.pairs_matched):
            if not self.pairs_matched[(word1, word2)]:
                continue
            item1 = QtWidgets.QTableWidgetItem(word1)
            item2 = QtWidgets.QTableWidgetItem(word2)
            item1.setToolTip(word1)
            item2.setToolTip(word2)
            item1.setBackground(self.color_match[(word1, word2)])
            item2.setBackground(self.color_match[(word1, word2)])
            self.table1.setItem(i, 0, item1)
            self.table2.setItem(i, 0, item2)

        for i, (word1, word2) in enumerate(color_no_match):
            item1 = QtWidgets.QTableWidgetItem(word1)
            item1.setToolTip(word1)
            item1.setBackground(self.match_to_color[self.new_background[word1]])
            for j in range(self.table1.rowCount()):
                item = self.table1.item(j, 0)
                if item and item.background().color() == item1.background().color():
                    self.table1.insertRow(j)
                    self.table1.setItem(j, 0, item1)
                    self.pairs_matched[(word1, self.new_background[word1])] = True
                    self.color_match[(word1, self.new_background[word1])] = item.background().color()
                    color_no_match.remove((word1, None))
                    self.table1.removeRow(self.table1.rowCount() - 1)
                    break
            
        for i, (word1, word2) in enumerate(unamtched_pairs_color):
            item1 = QtWidgets.QTableWidgetItem(word1)
            item2 = QtWidgets.QTableWidgetItem(word2)
            item1.setToolTip(word1)
            item2.setToolTip(word2)
            self.table1.setItem(i + total_pairs, 0, item1)
            self.table2.setItem(i + total_pairs_b, 0, item2)

        for i, (word1, _) in enumerate(unmatched1):
            item1 = QtWidgets.QTableWidgetItem(word1)
            item1.setToolTip(word1)
            self.table1.setItem(i + total_pairs + len(unamtched_pairs_color), 0, item1)

        for i, (_, word2) in enumerate(unmatched):
            item1 = QtWidgets.QTableWidgetItem(word2)
            item1.setToolTip(word2)
            self.table2.setItem(i + total_pairs_b + len(unamtched_pairs_color), 0, item1)

        #Resort the matched pairs
        # for j in range(self.table1.rowCount()):
        #     word1 = self.table1.item(j, 0).text()
        #     for i in range(j+1, self.table1.rowCount()):
        #         word2 = self.table1.item(i, 0).text()
        #         item1 = QtWidgets.QTableWidgetItem(word1)
        #         item2 = QtWidgets.QTableWidgetItem(word2)
        #         item1.setToolTip(word1)
        #         item2.setToolTip(word2)
        #         word1_bg = self.table1.item(j, 0).background().color()
        #         word2_bg = self.table1.item(i, 0).background().color()
        #         if word1_bg == word2_bg and (not is_white(word1_bg) and not is_white(word2_bg)):
        #             self.table1.insertRow(j)
        #             self.table1.setItem(j, 0, item2)
        #             item2.setBackground(word2_bg)
        #             self.table1.removeRow(self.table1.rowCount() - 1)

        # Adjust the tables to fit the content
        self.table1.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table1.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table1.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

        self.table2.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table2.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table2.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)'''