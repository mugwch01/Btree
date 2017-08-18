#My name is Charles Mugwagwa. 
#This is an implementation of a join query using recursive btrees.

import datetime
import os
from copy import deepcopy
import sys
import queue

class BTreeNode:
    '''
      This class will be used by the BTree class.  Much of the functionality of
      BTrees is provided by this class.
    '''
    def __init__(self, degree = 1, numberOfKeys = 0, items = None, child = None, \
        index = None):
        ''' Create an empty node with the indicated degree'''
        self.numberOfKeys = numberOfKeys
        if items != None:
            self.items = items
        else:
            self.items = [None]*2*degree
        if child != None:
            self.child = child
        else:
            self.child = [None]*(2*degree+1)
        self.index = index

    def __repr__(self):
        ''' This provides a way of writing a BTreeNode that can be
            evaluated to reconstruct the node.
        '''
        return "BTreeNode("+str(len(self.items)//2)+","+str(self.numberOfKeys)+ \
            ","+repr(self.items)+","+repr(self.child)+","+str(self.index)+")\n"

    def __str__(self):
        st = 'The contents of the node with index '+ \
             str(self.index) + ':\n'
        for i in range(0, self.numberOfKeys):
            st += '   Index   ' + str(i) + '  >  child: '
            st += str(self.child[i])
            st += '   item: '
            st += str(self.items[i]) + '\n'
        st += '                 child: '
        st += str(self.child[self.numberOfKeys]) + '\n'
        return st
    
    def isRootNode(self,node,bTree):
        return node.index == bTree.rootNode.index
    
    def __contains__(self,bTree,item):#write this contains
        def find_right_child(alist,item,numberOfItems):
            k = numberOfItems - 1
            while k >= 0 and item < alist[k]:                
                k -= 1
            return k        
        
        if item in self.items:
            return True
        else:
            if self.isLeafNode():
                return False
            else:                
                child_index = find_right_child(self.items,item,self.numberOfKeys)
                if self.child[child_index+1]==None:
                    return False
                else:
                    return bTree.nodes[self.child[child_index+1]].__contains__(bTree,item)   
        
    def isLeafNode(self):
        return self.child[0]== None           
    
    def insert(self,bTree,item):
        '''
        Insert an item in the node. Return three values as a tuple, 
        (left,item,right). If the item fits in the current node, then 
        return self as left and None for item and right. Otherwise, return 
        two new nodes and the item that will separate the two nodes in the parent. 
        ''' 
        
        def shiftRight(alist,item,numberOfItems):
            k = numberOfItems - 1
            while k >= 0 and item < alist[k]:
                alist[k+1] = alist[k]
                k -= 1
            return k            
                
        def find_right_child(alist,item,numberOfItems):
            k = numberOfItems - 1
            while k >= 0 and item < alist[k]:                
                k -= 1
            return k                    
            
        if self.isLeafNode() and not (self.isFull()):#leaf node and there is room
            k = shiftRight(self.items,item,self.numberOfKeys)
            self.items[k+1] = item
            self.numberOfKeys += 1
            return (self.index,None,None)
                            
        elif self.isLeafNode():#leaf node and it is full           
            right = None          
            node1,key,node2 = self.splitNode(bTree,item,right)                   
            return (node1,key,node2)      
        else:#non-leaf node            
            ##call insert recursively on the appropriate subtree.            
            child_index = find_right_child(self.items,item,self.numberOfKeys)             
            
            node1,key,node2 = bTree.nodes[self.child[child_index+1]].insert(bTree,item)
            if key == None:
                return (self.index,None,None)
            else:#newly promoted key and right subtree
                if self.isFull():
                    #split the node again as in step 2
                    right = None #leaf node         
                    node1,key,node2 = self.splitNode(bTree,key,right)                 
                    return (node1.index,key,node2.index)                    
                else:
                    k = shiftRight(self.items,key,self.numberOfKeys)
                    self.items[k+1] = key
                    self.numberOfKeys += 1
                    self.child[k+2] = node2 #recent addition
                    return (self.index,None,None)                   

    def splitNode(self,bTree,item,right):
        '''
        This method is given the item to insert into this node and the node 
        that is to be to the right of the new item once this node is split.
        
        Return the indices of the two nodes and a key with the item added to 
        one of the new nodes. The item is inserted into one of these two 
        nodes and not inserted into its children.
        '''
        
        def child_adjustments(part1_child,part2_child,sorted_list,right,item):             
            #making a list of all children for the sorted_list
            children = []            
            x = 1           
            children.append(self.child[0])            
            for i in range(len(sorted_list)):
                if sorted_list[i] == item:                    
                    children.append(right)
                else:
                    children.append(self.child[x])
                    x += 1    
                    
            #distributing the children between the two nodes
            index = 0 
            while index < len(children):
                if index < (len(children)/2):
                    alist = part1_child
                else:
                    alist = part2_child
                alist.append(children[index])
                index += 1                          
                
        def countKeys(alist):#count the number of not None items in a list
            count = 0
            for x in alist:
                if x != None:
                    count += 1
            return count
        
        def modify_org_list(org_list,new_list):
            count = 0
            for item in new_list:
                org_list[count] = item
                count += 1            
        
        #splitNode code starts here!        
        new_node = bTree.getFreeNode()        
        sorted_list = self.items[:]
        sorted_list.append(item)
        sorted_list.sort()        
        degree = bTree.degree
        part1 = sorted_list[:degree]+(degree*[None])#capacity has to be twice the degree       
        part1_child = []
        key = sorted_list[degree]
        part2 = sorted_list[degree+1:]+(degree*[None]) #capacity has to be twice the degree         
        part2_child = []
        #adjusting children
        child_adjustments(part1_child,part2_child,sorted_list,right,item)       
        #modifying actual nodes
        self.clear()
        self.items = part1        
        modify_org_list(self.child,part1_child)       
        self.numberOfKeys = countKeys(part1) 
        new_node.items = part2        
        modify_org_list(new_node.child,part2_child)
        new_node.numberOfKeys = countKeys(part2)        
        return (self.index,key,new_node.index)     
    
    def getLeftMost(self,bTree):
        ''' Return the left-most item in the 
            subtree rooted at self.
        '''
        if self.child[0] == None:
            return self.items[0]
        
        return bTree.nodes[self.child[0]].getLeftMost(bTree)

    def delete(self,bTree,item): #implement this delete
        '''
           The delete method returns None if the item is not found
           and a deep copy of the item in the tree if it is found.
           As a side-effect, the tree is updated to delete the item.
        '''          
        
        def find_right_child(alist,item,numberOfItems):
            k = numberOfItems - 1
            while k >= 0 and item < alist[k]:                
                k -= 1
            return k
        
        #delete code starts here!                   
        if item in self.items: #if item in this node
            if self.isLeafNode() and self.numberOfKeys > bTree.degree:                              
                self.items.remove(item)
                self.items = self.items+[None]
                self.numberOfKeys -= 1                
            elif self.isLeafNode() and self.numberOfKeys <= bTree.degree:              
                self.items.remove(item)
                self.items = self.items+[None]
                self.numberOfKeys -= 1                
                #rebalancing required                         
            else:#non-leaf node
                #the least value of the right subtree can replace the item in the node.
                item_index = self.items.index(item)
                right_subtree_index = item_index + 1
                right_subtree = bTree.nodes[self.child[right_subtree_index]]                
                #removing least value of the right subtree 
                replacement = right_subtree.items[0]
                right_subtree.delete(bTree,replacement) #recursive call
                self.items[item_index] = replacement
                
                #check if need rebalancing
                if right_subtree.numberOfKeys < bTree.degree:   
                    self.rebalance(right_subtree_index,bTree)    
                    
        else:#call delete on the right subtree            
            child_index = find_right_child(self.items,item,self.numberOfKeys)
            if self.child[child_index+1]==None:
                return
            bTree.nodes[self.child[child_index+1]].delete(bTree,item) 
            if bTree.nodes[self.child[child_index+1]].numberOfKeys < bTree.degree and not(self.isRootNode(bTree.nodes[self.child[child_index+1]],bTree)): #and not rootNode
                self.rebalance(child_index+1,bTree)                     
            
    def rebalance(self,unbalanced_node_index,bTree): #unbalanced_node_index = child[index] from self
        #parent_node = self
        unbalanced_node = bTree.nodes[self.child[unbalanced_node_index]]
        left_sibling_index = unbalanced_node_index - 1
        right_sibling_index = unbalanced_node_index + 1
        if self.child[left_sibling_index] != None:
            left_sibling = bTree.nodes[self.child[left_sibling_index]]
        if self.child[right_sibling_index] != None:
            right_sibling = bTree.nodes[self.child[right_sibling_index]]
        
        if self.child[left_sibling_index] != None and bTree.nodes[self.child[left_sibling_index]].numberOfKeys > bTree.degree:
            #rotate right
            x = left_sibling.items[left_sibling.numberOfKeys-1]
            parent_repl_index = left_sibling_index
            y = self.items[parent_repl_index]
            left_sibling.delete(bTree,x)
            self.items[parent_repl_index] = x
            unbalanced_node.insert(bTree,y)            
        elif self.child[right_sibling_index] != None and bTree.nodes[self.child[right_sibling_index]].numberOfKeys > bTree.degree:
            #rotate left
            x = right_sibling.items[0]
            parent_repl_index = unbalanced_node_index
            y = self.items[parent_repl_index]
            right_sibling.delete(bTree,x)
            self.items[parent_repl_index] = x
            unbalanced_node.insert(bTree,y)                    
        else: #coalescing    
            if self.child[left_sibling_index] != None:
                left_sibling.insert(bTree,self.items[left_sibling_index])
                while None in unbalanced_node.items:
                    unbalanced_node.items.remove(None)
                for k in unbalanced_node.items:                        
                    left_sibling.insert(bTree,k)
                unbalanced_node.clear()   
                self.child[unbalanced_node_index] = None 
                t = self.items[left_sibling_index]                        
                self.items.remove(t)
                self.items = self.items+[None]
                self.numberOfKeys -= 1 
            else:
                pass
                
    
    def redistributeOrCoalesce(self,bTree,childIndex):
        '''
          This method is given a node and a childIndex within 
          that node that may need redistribution or coalescing.
          The child needs redistribution or coalescing if the
          number of keys in the child has fallen below the 
          degree of the BTree. If so, then redistribution may
          be possible if the child is a leaf and a sibling has 
          extra items. If redistribution does not work, then 
          the child must be coalesced with either the left 
          or right sibling.

          This method does not return anything, but has the 
          side-effect of redistributing or coalescing
          the child node with a sibling if needed. 
        '''
        pass 


    def getChild(self,i):
        # Answer the index of the ith child
        if (0 <= i <= self.numberOfKeys):
            return self.child[i]
        else:
            print( 'Error in getChild().' )
            
    def setChild(self, i, childIndex):
        # Set the ith child of the node to childIndex
        self.child[i] = childIndex 

    def getIndex(self):
        return self.index

    def setIndex(self, anInteger):
        self.index = anInteger

    def isFull(self):
        ''' Answer True if the receiver is full.  If not, return
          False.
        '''
        return (self.numberOfKeys == len(self.items))

    def getNumberOfKeys(self):
        return self.numberOfKeys

    def setNumberOfKeys(self, anInt ):
        self.numberOfKeys = anInt

    def clear(self):
        self.numberOfKeys = 0
        self.items = [None]*len(self.items)
        self.child = [None]*len(self.child)

    def search(self, bTree, item):
        '''Answer a dictionary satisfying: at 'found'
          either True or False depending upon whether the receiver
          has a matching item;  at 'nodeIndex' the index of
          the matching item within the node; at 'fileIndex' the 
          node's index. nodeIndex and fileIndex are only set if the 
          item is found in the current node. 
        '''
        pass


class BTree:
    def __init__(self, degree, nodes = {}, rootIndex = 1, freeIndex = 2):
        self.degree = degree
        
        if len(nodes) == 0:
            self.rootNode = BTreeNode(degree)
            self.nodes = {}
            self.rootNode.setIndex(rootIndex)
            self.writeAt(1, self.rootNode)  
        else:
            self.nodes = deepcopy(nodes)
            self.rootNode = self.nodes[rootIndex]
              
        self.rootIndex = rootIndex
        self.freeIndex = freeIndex
        
    def __repr__(self):
        return "BTree("+str(self.degree)+",\n "+repr(self.nodes)+","+ \
            str(self.rootIndex)+","+str(self.freeIndex)+")"

    def __str__(self):
        st = '  The degree of the BTree is ' + str(self.degree)+\
             '.\n'
        st += '  The index of the root node is ' + \
              str(self.rootIndex) + '.\n'
        for x in range(1, self.freeIndex):
            node = self.readFrom(x)
            if node.getNumberOfKeys() > 0:
                st += str(node) 
        return st


    def delete(self, anItem):
        ''' Answer None if a matching item is not found.  If found,
          answer the entire item.
        ''' 
        
        self.rootNode.delete(self,anItem)
        
    def __contains__(self,item):
        return self.rootNode.__contains__(self,item)        

    def getFreeIndex(self):
        # Answer a new index and update freeIndex.  Private
        self.freeIndex += 1
        return self.freeIndex - 1

    def getFreeNode(self):
        #Answer a new BTreeNode with its index set correctly.
        #Also, update freeIndex.  Private
        newNode = BTreeNode(self.degree)
        index = self.getFreeIndex()
        newNode.setIndex(index)
        self.writeAt(index,newNode)
        return newNode

    def inorderOn(self, aFile):
        '''
          Print the items of the BTree in inorder on the file 
          aFile.  aFile is open for writing.
        '''
        aFile.write("An inorder traversal of the BTree:\n")
        self.inorderOnFrom( aFile, self.rootIndex)

    def inorderOnFrom(self, aFile, index):
        ''' Print the items of the subtree of the BTree, which is
          rooted at index, in inorder on aFile.
        '''
        pass

    def insert(self, anItem):#write this insert
        ''' Answer None if the BTree already contains a matching
          item. If not, insert a deep copy of anItem and answer
          anItem.
        '''
        
        node1,key,node2 = self.rootNode.insert(self,anItem) #indices return
        if key != None:
            new_parent_node = self.getFreeNode()
            new_parent_node.items[0] = key
            new_parent_node.child[0] = node1
            new_parent_node.child[1] = node2
            new_parent_node.numberOfKeys = 1
            self.rootNode = new_parent_node 

    def levelByLevel(self, aFile):
        ''' Print the nodes of the BTree level-by-level on aFile. )
        '''
        pass

    def readFrom(self, index):
        ''' Answer the node at entry index of the btree structure.
          Later adapt to files
        '''
        if self.nodes.__contains__(index):
            return self.nodes[index]
        else:
            return None

    def recycle(self, aNode):
        # For now, do nothing
        aNode.clear()

    def retrieve(self, anItem):
        ''' If found, answer a deep copy of the matching item.
          If not found, answer None
        '''
        pass

    def __searchTree(self, anItem):
        ''' Answer a dictionary.  If there is a matching item, at
          'found' is True, at 'fileIndex' is the index of the node
          in the BTree with the matching item, and at 'nodeIndex'
          is the index into the node of the matching item.  If not,
          at 'found' is False, but the entry for 'fileIndex' is the
          leaf node where the search terminated.
        '''
        pass

 
    def update(self, anItem):
        ''' If found, update the item with a matching key to be a
          deep copy of anItem and answer anItem.  If not, answer None.
        '''
        pass

    def writeAt(self, index, aNode):
        ''' Set the element in the btree with the given index
          to aNode.  This method must be invoked to make any
          permanent changes to the btree.  We may later change
          this method to work with files.
          This method is complete at this time.
        '''
        self.nodes[index] = aNode

def btreemain():
    print("My name is Charles Mugwagwa.")

    lst = [10,8,22,14,12,18,2,50,15]   
    
    b = BTree(2)
    
    for x in lst:
        print(repr(b))
        print("***Inserting",x)        
        b.insert(x)
        
    print(repr(b))
       
    lst = [14,50,8,12,18,2,10,22,15]
    
    alist = [14,50,8,12,18,2,10,22]
    lst = alist
    
    for x in lst:
        print("***Deleting",x)        
        b.delete(x) 
        print(repr(b))
        print("")
    
    #return 
    lst = [54,76]
    
    for x in lst:
        print("***Deleting",x)
        b.delete(x)
        print(repr(b))
        
    print("***Inserting 14")
    b.insert(14)
    
    print(repr(b))
    
    print("***Deleting 2")
    b.delete(2)
    
    print(repr(b))
    
    print ("***Deleting 84")
    b.delete(84)
    
    print(repr(b))
    

def readRecord(file,recNum,recSize):
    file.seek(recNum*recSize)
    record = file.read(recSize)
    return record

def readField(record,colTypes,fieldNum):
    # fieldNum is zero based
    # record is a string containing the record
    # colTypes is the types for each of the columns in the record
    
    offset = 0
    for i in range(fieldNum):
        colType = colTypes[i]
        
        if colType == "int":
            offset+=10
        elif colType[:4] == "char":
            size = int(colType[4:])
            offset += size
        elif colType == "float":
            offset+=20
        elif colType == "datetime":
            offset+=24

    colType = colTypes[fieldNum]

    if colType == "int":
        value = record[offset:offset+10].strip()
        if value == "null":
            val = None
        else:
            val = int(value)
    elif colType == "float":
        value = record[offset:offset+20].strip()
        if value == "null":
            val = None
        else:        
            val = float(value)
    elif colType[:4] == "char":
        size = int(colType[4:])
        value = record[offset:offset+size].strip()
        if value == "null":
            val = None
        else:        
            val = value[1:-1] # remove the ' and ' from each end of the string
            if type(val) == bytes:
                val = val.decode("utf-8") 
    elif colType == "datetime":
        value = record[offset:offset+24].strip()
        if value == "null":
            val = None
        else:        
            if type(val) == bytes:
                val = val.decode("utf-8") 
            val = datetime.datetime.strptime(val,'%m/%d/%Y %I:%M:%S %p')
    else:
        print("Unrecognized Type")
        raise Exception("Unrecognized Type") 
    
    return val

class Item:
    def __init__(self,key,value):
        self.key = key
        self.value = value
    
    def __repr__(self):
        return "Item("+repr(self.key)+","+repr(self.value)+")"

    def __eq__(self,other):
        if type(self) != type(other):
            return False

        return self.key == other.key
    
    def __lt__(self,other):
        return self.key < other.key
    
    def __gt__(self,other):
        return self.key > other.key
    
    def __ge__(self,other):
        return self.key >= other.key
    
    def getValue(self):
        return self.value
    
    def getKey(self):
        return self.key
            

def main():
    # Select Feed.FeedNum, Feed.Name, FeedAttribType.Name, FeedAttribute.Value where
    # Feed.FeedID = FeedAttribute.FeedID and FeedAttribute.FeedAtribTypeID = FeedAttribType.ID
    attribTypeCols = ["int","char20","char60","int","int","int","int"]
    feedCols = ["int","int","int","char50","datetime","float","float","int","char50","int"]
    feedAttributeCols = ["int","int","float"]
    
    feedAttributeTable = open("FeedAttribute.tbl","r")
    
    
    if os.path.isfile("Feed.idx"):
        indexFile = open("Feed.idx","r")
        feedTableRecLength = int(indexFile.readline())
        feedIndex = eval("".join(indexFile.readlines()))    

    else:
        feedIndex = BTree(3)
        feedTable = open("Feed.tbl","r")
        offset = 0
        for record in feedTable:
            feedID = readField(record,feedCols,0)
            anItem = Item(feedID,offset)
            feedIndex.insert(anItem)
            offset+=1
            feedTableRecLength = len(record)
         
        print("Feed Table Index Created")  
        indexFile = open("Feed.idx","w")
        indexFile.write(str(feedTableRecLength)+"\n")
        indexFile.write(repr(feedIndex)+"\n")
        indexFile.close()
    
    if os.path.isfile("FeedAttribType.idx"):
        indexFile = open("FeedAttribType.idx","r")
        attribTypeTableRecLength = int(indexFile.readline())
        attribTypeIndex = eval("".join(indexFile.readlines()))
    
    else: 
        attribTypeIndex = BTree(3)
        attribTable = open("FeedAttribType.tbl","r")
        offset = 0
        for record in attribTable:
            feedAttribTypeID = readField(record,attribTypeCols,0)
            anItem = Item(feedAttribTypeID,offset)
            attribTypeIndex.insert(anItem)
            offset+=1
            attribTypeTableRecLength = len(record)
         
        print("Attrib Type Table Index Created")
        indexFile = open("FeedAttribType.idx","w")
        indexFile.write(str(attribTypeTableRecLength)+"\n")
        indexFile.write(repr(attribTypeIndex)+"\n")
        indexFile.close()
    
    feedTable = open("Feed.tbl","rb")
    feedAttribTypeTable = open("FeedAttribType.tbl", "rb")
    before = datetime.datetime.now()
    for record in feedAttributeTable:
        
        feedID = readField(record,feedAttributeCols,0)
        feedAttribTypeID = readField(record,feedAttributeCols,1)
        value = readField(record,feedAttributeCols,2)
          
        lookupItem = Item(feedID,None)
        item = feedIndex.retrieve(lookupItem)
        offset = item.getValue()
        feedRecord = readRecord(feedTable,offset,feedTableRecLength)   
        feedNum = readField(feedRecord,feedCols,2)
        feedName = readField(feedRecord,feedCols,3)
        
        lookupItem = Item(feedAttribTypeID,None)
        item = attribTypeIndex.retrieve(lookupItem)
        offset = item.getValue()
        feedAttribTypeRecord = readRecord(feedAttribTypeTable,offset, \
            attribTypeTableRecLength)               
        feedAttribTypeName = readField(feedAttribTypeRecord,attribTypeCols,1)
        
        print(feedNum,feedName,feedAttribTypeName,value)
    after = datetime.datetime.now()
    deltaT = after - before
    milliseconds = deltaT.total_seconds() * 1000    
    print("Done. The total time for the query with indexing was",milliseconds, \
        "milliseconds.")
    
if __name__ == "__main__":
    btreemain()