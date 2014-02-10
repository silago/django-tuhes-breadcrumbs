# -*- coding: utf-8 -*-
from django.utils.importlib import import_module
from django.utils.functional import wraps
from django.core.urlresolvers import reverse
from django.db.models.query import QuerySet
VERSION	= '0.1'

def t_bread(field=None,	item_model=None,		foreignKey=None, foreignView=None,*args,**kwargs):	
	def add_crumb(field,item_model,foreignKey,foreignView,functionName,*args):
		key = args[0][0]
		fname =  functionName.__module__+"."+functionName.__name__
		if foreignView == True: foreignView=functionName
		element=item_model.objects.select_related().filter(**{field:key})[0]
		foreign_alias = getattr(element,field)
		e = {"url":reverse(fname, args=(foreign_alias,)),"name":(element.__unicode__())}
		cr =(e,)
		if foreignKey[1]:	cr = getSeflParent(item_model,field,foreignKey,fname,element)+cr if (foreignView==functionName) else foreignView(None,getattr(getattr(element,foreignKey[1]),foreignKey[0]))+cr
		return cr
	
	def getSeflParent(item_model,field,foreignKey,fname,element):
		foreign_alias = getattr(element,field)
		if element.parent == None: return ()
		element = getattr(element,foreignKey[1])
		key =  getattr(element,field)
		e = getSeflParent(item_model,field,foreignKey,fname,element)+({"url":reverse(fname, args=(key,)),"name":element.__unicode__()},)
		return e		

	def _bread(func):
		@wraps(func)
		def wrapper(request, *args, **kwargs):
			if field!=None:
				crumb =	add_crumb(field,item_model,foreignKey,foreignView,func,args)
			else: return  func(request,*args,**kwargs)
			if not request or request == None:	return crumb
			else:
				if not hasattr(request, 'bread'):	request.breads=()
				request.breads+=(crumb,)
				return	func(request,*args,**kwargs)
		return wrapper
	return _bread
