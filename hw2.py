from collections import deque

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

### Chi square table values ###
# The first key is the degree of freedom 
# The second key is the p-value cut-off
# The values are the chi-statistic that you need to use in the pruning

chi_table = {1: {0.5 : 0.45,
             0.25 : 1.32,
             0.1 : 2.71,
             0.05 : 3.84,
             0.0001 : 100000},
         2: {0.5 : 1.39,
             0.25 : 2.77,
             0.1 : 4.60,
             0.05 : 5.99,
             0.0001 : 100000},
         3: {0.5 : 2.37,
             0.25 : 4.11,
             0.1 : 6.25,
             0.05 : 7.82,
             0.0001 : 100000},
         4: {0.5 : 3.36,
             0.25 : 5.38,
             0.1 : 7.78,
             0.05 : 9.49,
             0.0001 : 100000},
         5: {0.5 : 4.35,
             0.25 : 6.63,
             0.1 : 9.24,
             0.05 : 11.07,
             0.0001 : 100000},
         6: {0.5 : 5.35,
             0.25 : 7.84,
             0.1 : 10.64,
             0.05 : 12.59,
             0.0001 : 100000},
         7: {0.5 : 6.35,
             0.25 : 9.04,
             0.1 : 12.01,
             0.05 : 14.07,
             0.0001 : 100000},
         8: {0.5 : 7.34,
             0.25 : 10.22,
             0.1 : 13.36,
             0.05 : 15.51,
             0.0001 : 100000},
         9: {0.5 : 8.34,
             0.25 : 11.39,
             0.1 : 14.68,
             0.05 : 16.92,
             0.0001 : 100000},
         10: {0.5 : 9.34,
              0.25 : 12.55,
              0.1 : 15.99,
              0.05 : 18.31,
              0.0001 : 100000},
         11: {0.5 : 10.34,
              0.25 : 13.7,
              0.1 : 17.27,
              0.05 : 19.68,
              0.0001 : 100000}}


def calc_gini(data):
    """
    Calculate gini impurity measure of a dataset.

    Input:
    - data: any dataset where the last column holds the labels.

    Returns:
    - gini: The gini impurity value.
    """
    gini = 0.0
    ###########################################################################
    # TODO: Implement the function.                                           #
    ###########################################################################
    labels = data[:, -1]
    label_counts = pd.Series(labels).value_counts().to_dict()
    total = len(labels)

    for label in label_counts:
        gini += (label_counts[label] / total) ** 2

    gini = 1 - gini
    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################
    return gini


def calc_entropy(data):
    """
    Calculate the entropy of a dataset.

    Input:
    - data: any dataset where the last column holds the labels.

    Returns:
    - entropy: The entropy value.
    """
    entropy = 0.0
    ###########################################################################
    # TODO: Implement the function.                                           #
    ###########################################################################
    labels = data[:, -1]
    label_counts = pd.Series(labels).value_counts().to_dict()
    total = len(labels)

    for label in label_counts:
        if label_counts[label] > 0:
            entropy += (label_counts[label] / total) * np.log2(label_counts[label] / total)
        else:
            print("Feature {} has no children.".format(label))
    entropy = -1 * entropy
    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################
    return entropy

class DecisionNode:

    
    def __init__(self, data, impurity_func, feature=-1,depth=0, chi=1, max_depth=1000, gain_ratio=False):
        
        self.data = data # the data instances associated with the node
        self.terminal = False # True iff node is a leaf
        self.feature = feature # column index of feature/attribute used for splitting the node
        self.pred = self.calc_node_pred() # the class prediction associated with the node
        self.depth = depth # the depth of the node
        self.children = [] # the children of the node (array of DecisionNode objects)
        self.children_values = [] # the value associated with each child for the feature used for splitting the node
        self.max_depth = max_depth # the maximum allowed depth of the tree
        self.chi = chi # the P-value cutoff used for chi square pruning
        self.impurity_func = impurity_func # the impurity function to use for measuring goodness of a split
        self.gain_ratio = gain_ratio # True iff GainRatio is used to score features
        self.feature_importance = 0
    
    def calc_node_pred(self):
        """
        Calculate the node's prediction.

        Returns:
        - pred: the prediction of the node
        """
        pred = None
        ###########################################################################
        # TODO: Implement the function.                                           #
        ###########################################################################
        labels = self.data[:, -1]
        values, counts = np.unique(labels, return_counts=True)
        pred = values[np.argmax(counts)]
        ###########################################################################
        #                             END OF YOUR CODE                            #
        ###########################################################################
        return pred
        
    def add_child(self, node, val):
        """
        Adds a child node to self.children and updates self.children_values

        This function has no return value
        """
        ###########################################################################
        # TODO: Implement the function.                                           #
        ###########################################################################
        self.children.append(node)
        self.children_values.append(val)
        ###########################################################################
        #                             END OF YOUR CODE                            #
        ###########################################################################
    
    def goodness_of_split(self, feature):
        """
        Calculate the goodness of split of a dataset given a feature and impurity function.

        Input:
        - feature: the feature index the split is being evaluated according to.

        Returns:
        - goodness: the goodness of split
        - groups: a dictionary holding the data after splitting 
                  according to the feature values.
        """
        goodness = 0
        groups = {} # groups[feature_value] = data_subset
        ###########################################################################
        # TODO: Implement the function.                                           #
        ###########################################################################
        phi_s = self.impurity_func(self.data)
        values = list(np.unique(self.data[:, feature]))

        total_rows = len(self.data)
        summ_of_impurities = 0.0
        for val in values:
            groups[val] = self.data[self.data[:, feature] == val]
            impurity = (groups[val].shape[0] / total_rows) * self.impurity_func(groups[val])
            summ_of_impurities += impurity
        goodness = phi_s - summ_of_impurities

        # Compute split info for gain ratio
        if self.gain_ratio:
            split_info = 0.0
            for subset in groups.values():
                p = len(subset) / total_rows
                if p > 0:
                    split_info -= p * np.log2(p)
            if split_info > 0:
                gain_ratio = goodness / split_info
            else:
                gain_ratio = 0.0
            return gain_ratio, groups
        ###########################################################################
        #                             END OF YOUR CODE                            #
        ###########################################################################
        return goodness, groups
        
    def calc_feature_importance(self, n_total_sample):
        """
        Calculate the selected feature importance.
        
        Input:
        - n_total_sample: the number of samples in the dataset.

        This function has no return value - it stores the feature importance in 
        self.feature_importance
        """
        ###########################################################################
        # TODO: Implement the function.                                           #
        ###########################################################################
        total_rows = len(self.data)
        goodness, _ = self.goodness_of_split(self.feature)
        self.feature_importance = (total_rows / n_total_sample) * goodness
        ###########################################################################
        #                             END OF YOUR CODE                            #
        ###########################################################################
    
    def split(self):
        """
        Splits the current node according to the self.impurity_func. This function finds
        the best feature to split according to and create the corresponding children.
        This function should support pruning according to self.chi and self.max_depth.

        This function has no return value
        """
        ###########################################################################
        # TODO: Implement the function.                                           #
        ###########################################################################

        # Find the maximal feature according to the goodness of split
        max_goodness = -float('inf')
        max_feature = None
        max_feature_subset = None

        n_features = self.data.shape[1] - 1  # Do not include the last column, which are the labels

        for feature in range(n_features):
            goodness, groups = self.goodness_of_split(feature)
            if goodness > max_goodness:
                max_goodness = goodness
                max_feature = feature
                max_feature_subset = groups

        if max_goodness <= 0 or self.depth >= self.max_depth:
            self.terminal = True
            return

        if self.chi < 1.0:  # Only prune if chi pruning is active
            n_classes = len(np.unique(self.data[:, -1]))
            degrees_of_freedom = (len(max_feature_subset) - 1) * (n_classes - 1)
            chi_square = self.compute_chi_square(max_feature_subset)
            chi_threshold = chi_table[degrees_of_freedom][self.chi]

            if chi_square < chi_threshold:
                self.terminal = True
                return

        self.feature = max_feature

        # Create the nodes for each child (value) of the maximal feature
        for val, subset in max_feature_subset.items():
            child_node = DecisionNode(
                subset, self.impurity_func, depth=self.depth + 1,
                chi=self.chi, max_depth=self.max_depth, gain_ratio=self.gain_ratio
            )
            self.add_child(child_node, val)

        # If no children, it's a leaf
        if len(self.children) == 0:
            self.terminal = True

    def compute_chi_square(self, groups):
        """
        Computes the chi-squared statistic between parent and children groups.

        Input:
        - groups: dict mapping feature value -> subset of the data

        Output:
        - chi-square statistic (float)
        """

        n_classes = len(np.unique(self.data[:, -1]))
        df = (len(groups) - 1) * (n_classes - 1)

        # Parent label distribution
        labels = self.data[:, -1]
        parent_counts = pd.Series(labels).value_counts().to_dict()
        total_parent = len(labels)

        chi_square = 0.0

        for subset in groups.values():
            subset_labels = subset[:, -1]
            subset_counts = pd.Series(subset_labels).value_counts().to_dict()
            total_subset = len(subset_labels)

            for label in parent_counts:
                expected = (parent_counts[label] / total_parent) * total_subset
                observed = subset_counts.get(label, 0)
                if expected > 0:
                    chi_square += (observed - expected) ** 2 / expected

        return chi_square
        ###########################################################################
        #                             END OF YOUR CODE                            #
        ###########################################################################

                    
class DecisionTree:
    def __init__(self, data, impurity_func, feature=-1, chi=1, max_depth=1000, gain_ratio=False):
        self.data = data # the training data used to construct the tree
        self.root = None # the root node of the tree
        self.max_depth = max_depth # the maximum allowed depth of the tree
        self.chi = chi # the P-value cutoff used for chi square pruning
        self.impurity_func = impurity_func # the impurity function to be used in the tree
        self.gain_ratio = gain_ratio #
        
    def depth(self):
        return self.root.depth

    def build_tree(self):
        """
        Build a tree using the given impurity measure and training dataset. 
        You are required to fully grow the tree until all leaves are pure 
        or the goodness of split is 0.

        This function has no return value
        """
        self.root = None
        ###########################################################################
        # TODO: Implement the function.                                           #
        ###########################################################################
        self.root = DecisionNode(
            self.data,
            impurity_func=self.impurity_func,
            max_depth=self.max_depth,
            chi=self.chi,
            gain_ratio=self.gain_ratio
        )
        queue = deque([self.root]) # initialize queue with root node
        import time

        count = 0
        start = time.time()

        while len(queue) > 0:
            node = queue.popleft()
            node.split()
            for child in node.children:
                queue.append(child)
            count += 1

            if count % 500 == 0:
                elapsed = time.time() - start
                print(f"Processed {count} nodes in {elapsed:.1f}s; queue size = {len(queue)}")
        ###########################################################################
        #                             END OF YOUR CODE                            #
        ###########################################################################

    def predict(self, instance):
        """
        Predict a given instance
     
        Input:
        - instance: a row vector from the dataset. Note that the last element
                    of this vector is the label of the instance.
     
        Output: the prediction of the instance.
        """
        pred = None
        ###########################################################################
        # TODO: Implement the function.                                           #
        ###########################################################################
        node = self.root
        while not node.terminal:
            value = instance[node.feature]
            found = False
            for i in range(len(node.children_values)):
                if node.children_values[i] == value:
                    node = node.children[i]
                    found = True
                    break
            if not found:
                break  # unknown value — stop early
        ###########################################################################
        #                             END OF YOUR CODE                            #
        ###########################################################################
        return node.pred

    def calc_accuracy(self, dataset):
        """
        Predict a given dataset 
     
        Input:
        - dataset: the dataset on which the accuracy is evaluated
     
        Output: the accuracy of the decision tree on the given dataset (%).
        """
        accuracy = 0
        ###########################################################################
        # TODO: Implement the function.                                           #
        ###########################################################################
        for row in dataset:
            prediction = self.predict(row)
            if prediction == row[-1]:
                accuracy += 1
        accuracy /= len(dataset)
        accuracy *= 100
        ###########################################################################
        #                             END OF YOUR CODE                            #
        ###########################################################################
        return accuracy
        

def depth_pruning(X_train, X_validation):
    """
    Calculate the training and validation accuracies for different depths
    using the best impurity function and the gain_ratio flag you got
    previously. 

    Input:
    - X_train: the training data where the last column holds the labels
    - X_validation: the validation data where the last column holds the labels
 
    Output: the training and validation accuracies per max depth
    """
    training = []
    validation  = []
    root = None
    best_impurity = get_best_impurity(X_train, X_validation)

    for max_depth in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
        ###########################################################################
        # TODO: Implement the function.                                           #
        ###########################################################################
        if best_impurity == 'gini':
            tree = DecisionTree(
                X_train,
                impurity_func=calc_gini,
                max_depth=max_depth,
            )
        elif best_impurity == 'entropy':
            tree = DecisionTree(
                X_train,
                impurity_func=calc_entropy,
                max_depth=max_depth,
            )
        elif best_impurity == 'gini_gain':
            tree = DecisionTree(
                X_train,
                impurity_func=calc_gini,
                max_depth=max_depth,
                gain_ratio=True,
            )
        else:
            tree = DecisionTree(
                X_train,
                impurity_func=calc_entropy,
                max_depth=max_depth,
                gain_ratio=True,
            )

        tree.build_tree()
        training.append(tree.calc_accuracy(X_train))
        validation.append(tree.calc_accuracy(X_validation))
        ###########################################################################
        #                             END OF YOUR CODE                            #
        ###########################################################################
    return training, validation


def chi_pruning(X_train, X_test):

    """
    Calculate the training and validation accuracies for different chi values
    using the best impurity function and the gain_ratio flag you got
    previously. 

    Input:
    - X_train: the training data where the last column holds the labels
    - X_validation: the validation data where the last column holds the labels
 
    Output:
    - chi_training_acc: the training accuracy per chi value
    - chi_validation_acc: the validation accuracy per chi value
    - depth: the tree depth for each chi value
    """
    chi_training_acc = []
    chi_validation_acc  = []
    depth = []

    ###########################################################################
    # TODO: Implement the function.                                           #
    ###########################################################################
    # decide which impurity to use
    best_impurity = get_best_impurity(X_train, X_test)
    if best_impurity.startswith('gini'):
        impurity = calc_gini
    else:
        impurity = calc_entropy
    use_gain = best_impurity.endswith('_gain')

    # iterate over the standard p-value cutoffs in your chi_table
    p_values = sorted(chi_table[1].keys())  # [0.0001, 0.05, 0.1, 0.25, 0.5]
    for p in p_values:
        # build tree with this chi cutoff
        tree = DecisionTree(
            X_train,
            impurity_func=impurity,
            chi=p,
            max_depth=1000,  # effectively unbounded; pruning comes from chi
            gain_ratio = use_gain
        )
        tree.build_tree()

        # record accuracies
        chi_training_acc.append(tree.calc_accuracy(X_train))
        chi_validation_acc.append(tree.calc_accuracy(X_test))

        # compute maximal depth of the built tree
        max_d = 0
        queue = deque([tree.root])
        while queue:
            node = queue.popleft()
            max_d = max(max_d, node.depth)
            for c in node.children:
                queue.append(c)
        depth.append(max_d)
    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################
        
    return chi_training_acc, chi_validation_acc, depth


def count_nodes(node):
    """
    Count the number of node in a given tree
 
    Input:
    - node: a node in the decision tree.
 
    Output: the number of node in the tree.
    """
    ###########################################################################
    # TODO: Implement the function.                                           #
    ###########################################################################
    n_nodes = 0
    queue = deque([node])
    while queue:
        node = queue.popleft()
        n_nodes += 1
        for c in node.children:
            queue.append(c)
    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################
    return n_nodes


def get_best_impurity(X_train, X_validation):
    gini_tree = DecisionTree(
        X_train,
        impurity_func=calc_gini,
    )

    entropy_tree = DecisionTree(
        X_train,
        impurity_func=calc_entropy,
    )

    gini_tree_gain = DecisionTree(
        X_train,
        impurity_func=calc_gini,
        gain_ratio=True,
    )

    entropy_tree_gain = DecisionTree(
        X_train,
        impurity_func=calc_entropy,
        gain_ratio=True,
    )

    gini_tree.build_tree()
    entropy_tree.build_tree()
    gini_tree_gain.build_tree()
    entropy_tree_gain.build_tree()

    gini_acc = gini_tree.calc_accuracy(X_validation)
    entropy_acc = entropy_tree.calc_accuracy(X_validation)
    gini_acc_gain = gini_tree_gain.calc_accuracy(X_validation)
    entropy_acc_gain = entropy_tree_gain.calc_accuracy(X_validation)

    func2acc = {}
    func2acc['gini'] = gini_acc
    func2acc['entropy'] = entropy_acc
    func2acc['gini_gain'] = gini_acc_gain
    func2acc['entropy_gain'] = entropy_acc_gain

    return max(func2acc, key=func2acc.get)





